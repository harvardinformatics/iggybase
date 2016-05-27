from blinker import signal
from threading import Timer, Semaphore
from datetime import datetime, date, timedelta
import logging
import flask

from sqlalchemy import event
from sqlalchemy.engine import reflection
from sqlalchemy.util.langhelpers import symbol
from flask_mail import Attachment, Connection, Message, Mail

event_registry = {}

_hb = {'interval': 15, 'func': None}

_pv_semaphore = Semaphore()

def _event_pitcher(sender, **kw):
    """Dispatches databse events to be processed
    act_obj must have an execute method
    """
    _pv_semaphore.acquire()
    sender.execute(**kw)
    _pv_semaphore.release()
    return


def _heartbeat():
    """
    Called in a separate thread every basic interval (_hb['interval']).
    periodic actions are dispatched by an internal action (HBAction).
    The event_registry is accessed by means of PV semaphores
    """
    _pv_semaphore.acquire()
    evt = event_registry.get('heartbeat-action', None)[0]   # Should only be one.
    t = Timer(_hb['interval'], _hb['func'])
    t.start()
    _pv_semaphore.release()        

    evt.dispatch(obj=evt, event_type='heartbeat-action')

def db_event(session, stat, instances):
    """Dispatcher for database events
    """
    def event_scan(session_itr):
        """Scans the event objects (db table create/update/delete actions).
        """
        for obj in session_itr:
            evt_name = getattr(obj, '__tablename__', None)
            model_name = '%s:%s' % (evt_cat, evt_name)
            specific = '%s:%s:%s' % (evt_cat, evt_name, evt_type)
            _pv_semaphore.acquire()
            key_combo = set([evt_cat, model_name, specific])

            registry_keys = set(event_registry.keys())
            _pv_semaphore.release()
            outcomes = list(key_combo & registry_keys)

            for kk in outcomes:
                _pv_semaphore.acquire()                
                actions = event_registry.get(kk, None)
                _pv_semaphore.release()
                # Shouldn't happen possible keys were anded with registry entries.
                if not actions:
                    continue

                for action in actions:
                    if action.verify(obj, evt_type):
                        action.dispatch(obj, event_type=evt_type)

    evt_cat = 'database'

    if session.deleted:
        evt_type = 'deleted'
        event_scan(session.deleted)
    if session.new:
        evt_type = 'new'
        event_scan(session.new)
    if session.dirty:
        evt_type = 'dirty'
        event_scan(session.dirty)


def db_attr_event(target, value, oldvalue, initiator):
    """
    Find the appropriate object and verify.
    Dispatch if necessary.
    """
    op = 'new' if oldvalue == symbol('NO_VALUE') else 'dirty'

    reg_key = 'database:%s:%s:%s' % (target.__tablename__, initiator.key, op)
    _pv_semaphore.acquire()    
    actions = event_registry.get(reg_key, None)
    _pv_semaphore.release()    
    kwargs = {'newvalue': value, 'oldvalue': oldvalue}
    if actions:
        for action in actions:
            if action.verify(target, op, **kwargs):
                action.dispatch(target, op, **kwargs)

    return target



def db_rollback(session):
    print('rolled back')


def init_app(app, session):
    if hasattr(app, 'act_manager'):
        return app.act_manager
    app.act_manager = ActionManager(app, session)



class ActionManager(object):
    """
    Instantiated after app initialization. Store instance globally and use it to
    register actions. Session and app must be provided.
    """
    name = 'Action Manager'
    description = 'Base Action Manager'


    def __init__(self, app, session):
        self.app = app
        self.session = session
        self._action_signal = signal('action_signal')
        self._action_signal.connect(_event_pitcher)
        if not hasattr(app, 'act_manager'):
            app.act_manager = self

        # Guarantee Idempotence. Database events
        if event.contains(self.session, 'before_flush', db_event):
            return
        event.listen(self.session, 'before_flush', db_event)

        if event.contains(self.session, 'after_rollback', db_rollback):
            return
        event.listen(self.session, 'after_rollback', db_rollback)

        # Don't need to worry about threads yet since the _heartbeat thread
        # isn't running.
        _ha = HeartbeatAction()
        if not _ha:
            raise ValueError()
        
        event_registry.setdefault('heartbeat-action', []).append(_ha)

        # Periodic events. Smallest periodic interval is 15 seconds. Could be
        # configurable.
        _hb['func'] = _heartbeat
        t = Timer(_hb['interval'], _hb['func'])
        t.start()
        
        


    def register_db_event(self, action):
        """Registers an action's event.

        The event is identified by category, name, and type. The
        Categories are: database
        For database events:
             model,
             field_name,
             event_type is one of new|delete|dirty
        """
        action.act_manager = self
        
        valid_categories = ['database']
        valid_event_types = ['new', 'deleted', 'dirty']

        # The registry is a flat dict by combining category and name.
        k = 'database'    # Database event

        if action.model:
            k = k + ':' + action.model.__tablename__
        else:
            raise ValueError('%s must be a valid model' % action.model)

        if action.field_name:
            k = k + ':' + action.field_name

        if action.event_type not in valid_event_types:
            raise ValueError( '%s is not a valid event type %s, %s' % \
                              (action.event_type, k, str(valid_event_types)))
        k = k + ':' + action.event_type

        # The registry: keys are like: 'database-model-field_name-dirty'
        # Don't allow dupes. Make this idempotent.
        _pv_semaphore.acquire()
        if k not in event_registry:
            event_registry.setdefault(k, []).append(action)
        else:
            if self.action in event_registry[k]:
                logging.debug('duplicate action register rejected, %s' % repr(action))
            else:
                logging.info('action registered, %s' % action.name)
                event_registry[k].append(action)
        _pv_semaphore.release()


        # The listener needs the model.attribute such as: User.first_name
        if action.model and action.field_name and action.event_type == 'dirty':
            collection = getattr(action.model, action.field_name)
            # Guarantee Idempotence by not repeateing this event.
            if event.contains(collection, 'set', db_attr_event):
                return
            event.listen(collection, 'set', db_attr_event)


        


    def register_periodic_event(self, action):
        """
        Register a periodic action.
        """
        action.act_manager = self
        sod = datetime.now().date()
        sod = datetime(sod.year, sod.month, sod.day)
        action.next_p =  sod + action.from_time
        action.latest_p = sod +  action.to_time
        #register the action, it's times and trigger count.
        reg = {'action': action, 'count': 0, 'nxt': action.next_p, 'latest': action.latest_p}
        _pv_semaphore.acquire()        
        event_registry.setdefault('periodic', []).append(reg)
        _pv_semaphore.release()            


    def unregister(self, action):
        """ToDo
        """
        return True


class VerifyObject(object):
    """Base class for objects to verify.

    """
    def __init__(self, **kwargs):
        self.lookups = {}
        if kwargs:
            for k,v in kwargs.items():
                setattr(self, k, v)


    def load_params(self, tablename, fieldname, keyname, rows):
        """
        Load db rows into a searchable set of nested dicts:
            { 'tablename': { 'fieldname' : { 'id': value }, ... }, ... }
        """
        table_level = self.lookups.setdefault(tablename, {})
        name_level = table_level.setdefault(fieldname, {})
        for row in rows:
            id = getattr(row, keyname, None)
            name_level[id] = getattr(row, fieldname, None)



    def add_param(self, tablename, fieldname, keyname, row):
        """Add a new entry to the verifiable params
        """
        self.load_params(tablename, fieldname, keyname, [row])


    def delete_param(self, tablename, fieldname, keyname):

        try:
            table_level = self.lookups[tablename]
            name_level = table_level[fieldname]
            name_level.pop(keyname)
            if len(name_level) == 0:
                table_level.pop(fieldname)
            if len(table_level) == 0:
                self.lookups.pop(tablename)

        except KeyError:
            print('Error deleting value %s from row with key %s from table %s' \
                  % (fieldname, keyname, tablename))
            return

    def update_param(self, tablename, fieldname, keyname, newval):
        try:
            table_level = self.lookups[tablename]
            name_level = table_level[fieldname]
            name_level[keyname] = newval

        except KeyError:
            print('Error updating value %s in row with key %s, table %s' \
                               % (fieldname, keyname, tablename))
            return


    def search_params(self, obj):
        tablename = obj.__tablename__
        table_level = self.lookups[tablename]
        name, vals = table_level.items()[0]
        try:
            new_val = vals[obj.id]
            if new_val != getattr(obj, name):
                return 'changed'
            else:
                return 'unchanged'
        except KeyError:
            return 'not found'




class Action(object):
    """Base class for actions.
    Events are database, cron, or application specified.
    For database events, names are:
        model - the model. There no other way to import it.
        field_name - field_name
        event_type - new, delete, or dirty.

    default: database
    """
    name = 'Action'
    description = 'Base class for database events.'
    act_manager = None  # Assigned when registered to an event.

    def __init__(self, cat='database', model=None, field_name=None,
                 event_type='dirty', 
                 verify_callback=None,
                 execute_callback=None,
                 **kwargs):
        """
        verify_params (kwargs) are used by the verify method to further test the
        validity of an event.
        """
        if not hasattr(self, 'cat'):
            if not cat:
                raise ValueError('category cannot be None')
            self.event_category = cat

        if cat == 'database':

            if not hasattr(self, 'model'):
                self.model = model

            if not hasattr(self, 'field_name'):
                self.field_name = field_name

            if not hasattr(self, 'event_type'):
                if event_type not in ['new', 'dirty', 'delete']:
                    raise ValueError('event_type cannut be null')
                else:
                    self.event_type = event_type
            if not hasattr(self, 'verify_callback'):
                self.verify_callback = verify_callback

            if not hasattr(self, 'execute_callback'):
                self.execute_callback = execute_callback

            if kwargs:
                for k,v in kwargs.items():
                    setattr(self, k, v)
            keys = kwargs.keys()

            if 'tablename' in keys and 'fieldname' in keys and 'keyname' in keys \
               and 'rows' in keys:
                if self.tablename and self.fieldname and self.keyname and self.rows:
                    self.lookups = VerifyObject()
                    self.lookups.load_params(self.tablename, self.fieldname,
                                                   self.keyname, self.rows)

                
    def __eq__(self, obj):
        if self.__dict__ == obj.__dict__:
            return True
        else:
            return False

                                      

    def verify(self, obj, evt_type, **kwargs):
        """Validate event.
        Returning False means the event is a don't care.
        Otherwise, returning True (default)  validates the object.
        It can then be either call the execute method. Or, it can return True
        and the execute will be dispatched via a signal maybe in another thread.
        """
        if hasattr(self, 'verify_callback') and self.verify_callback:
            return self.verify_callback(obj, evt_type, **kwargs)
        else:
            return True


    def load_params(self, tablename, fieldname, keyname, rows):
        """Load parameters to verify.
        The verify parameters may also be loaded when initiating the Action object.
        """
        if tablename and fieldname and keyname and rows:

            self.tablename = tablename
            self.fieldname = fieldname
            self.keyname = keyname

            self.verify_object = VerifyObject()
            self.verify_object.load_params(tablename, fieldname, keyname, rows)
        else:
            raise ValueError('Missing params')
        return



    def dispatch(self, obj, event_type, **kwargs):
        """Enqueue the object for a signal.
        False return means nothing enqueued.
        """
        kwargs['obj'] = obj
        pitcher = signal('action_signal')
        logging.debug('sending signal with kwargs=%s' % (kwargs))
        pitcher.send(self, **kwargs)

    def execute(self, obj, **kwargs):
        """execute the action"""
        logging.debug('obj=%s, kwargs=%s' % (repr(obj), repr(kwargs)))
        if hasattr(self, 'execute_callback') and self.execute_callback:
            self.execute_callback(obj, event_type, kwargs)
        return


class HeartbeatAction(Action):
    """
    Used to dispatch periodic (heartbeat) events.
    """
    name = 'Heartbeat Action'
    description = 'Dispatches periodic actions.'
    cat = 'heartbeat-action'
    
    def execute(self, obj, **kwargs):
        """
        Dispatch periodic events. Periodic events are locked out
        while actions are dispatched. 
        """
        evts = event_registry.get('periodic', [])

        for evt in evts:
            action = evt['action']
            count = evt['count']
            nxt = evt['nxt']
            latest = evt['latest']
            print(action, count, nxt, latest)
            now = datetime.now()
            if count <= action.dispatch_count and now >= nxt and now <= latest:
                if action.verify(evt, evt_type='periodic', **kwargs):
                    print('dispatching %s' % evt)
                    try:  
                        action.dispatch(**evt)
                    except:
                        # return even if ther was an error so the thread releases.
                        return
                    action.dispatch_count += 1
                    action.previous_p = nxt
                    action.next_p += action.interval
                    evt['nxt'] = action.next_p
                    evt['count'] += 1

        
    


class PeriodicAction(Action):
    """Class for actions taken based on periodic intervals, starting and ending
    between two timedeltas from the beginning of a day. For example: every hour
    starting at 2:30 until 16:30.
    """
    name = 'Periodic Action'
    description = 'Action triggered by time periods.'
    cat = 'periodic'

    period = 1
    period_unit = 'hour'
    from_time = timedelta(0)
    to_time = timedelta(hours=23, minutes=59, seconds=59)

    dispatch_count = 0
    previous_p = None
    next_p = None
    latest_p = None
    interval = None

    
    def __init__(self, *args, **kwargs):
        """
        """
        super(PeriodicAction,self).__init__(cat=self.cat, *args, **kwargs)
        if self.period_unit == 'sec':
            base = 1
        elif self.period_unit == 'minute':
            base = 60
        elif self.period_unit == 'hour':
            base = 60*60
        else:                # Make it a day.
            base = 60*60*24      

        self.interval = timedelta(seconds=base*self.period)




class EmailAction(Action):

    log_mail = False

    def __init__(self, *args, **kwargs):
        """kwargs may contain email Message fields.

        If a message field is not provided as a parameter, that field's name, say - bcc,
        can be derived by overidding the get_bcc method below or any one of the 'get_' 
        methods that corresponds to a Message field.

        Fields not supported: html, extra_headers, mail_options, rcpt_options.
        Permitted fields are get_* method names below with "get_" removed such as:
            subject
            recipients
            text
        """
        Action.__init__(self, *args, **kwargs)


    def get_subject(self, **kwargs):
        """
        Email subject string.
        Override to provide object's subject
        """
        if hasattr(self, 'subject'):
            return getattr(self, 'subject', None)
        return None

    def get_recipients(self, **kwargs):
        """
        Recipients list
        """
        if hasattr(self, 'recipients'):
            return getattr(self, 'recipients', None)
        return None

    def get_cc(self, **kwargs):
        if hasattr(self, 'cc'):
            return getattr(self, 'cc', None)
        return None

    def get_bcc(self, **kwargs):
        if hasattr(self, 'bcc'):
            return getattr(self, 'bcc', None)
        return None

    def get_body(self, **kwargs):
        """
        Body consists of text and context as:
            {'body': { 'text': ..., 'context': ... }}

        """
        if hasattr(self, 'body'):
            return self.render_from_text(getattr(self, 'body', None))
        return None

    def get_attachments(self, **kwargs):
        """
        Attachment list expects a list of dicts with:
            filename=filename,
            content_type=content_type,  (mime_type)
            data=data,
        """
        attchs = []
        if hasattr(self, 'attachments'):
            for attach in getattr(self, 'attachments'):
                attchs.append(Attachment(attach))
            return attchs
        return None

    def get_reply_to(self, **kwargs):
        if hasattr(self, 'reply_to'):
            return getattr(self, 'reply_to', None)
        return None

    def get_charset(self, **kwargs):
        if hasattr(self, 'charset'):
            return getattr(self, 'charset', None)
        return None


    def execute(self, **kwargs):
        """
        Send email message
        """
        from . import actions
        with self.act_manager.app.app_context():
            if self.act_manager.app.debug == True:
                msg = Message(sender='reuven@koblick.com')
            for func in [getattr(self, aa) for aa in dir(self) if aa.startswith('get_')]:
                result = func(**kwargs)
                if result:
                    head, sep, tail = func.__name__.partition('_')
                    if tail == 'attachments':
                        for attachment in result:
                            msg.add_attachment(attachment)
                    else:
                        setattr(msg, tail, result)

            mail = Mail(self.act_manager.app)
            mail.connect()
            mail.send(msg)
            if self.log_mail:
                """
                Log email to a table with a timestamp. Note, for attachements, don't only log the
                file name and content_type, not the data.
                """
                pass
        return

    def render_from_text(self, ctx):
        """
        ctx is { 'text': ...,  'context': { ... } }
        """
        from jinja2 import Template

        template = Template(ctx['text'])
        return template.render(ctx['context'])


    def render_from_template(self, ctx, environ):
        """
        Mail environment must be valid in order to find the
        template in the file system.
        ctx is { 'template': xxx.html, 'context': { ... } }
        """
        template = environ.get_template(ctx['template'])
        return template.render(ctx['context'])
