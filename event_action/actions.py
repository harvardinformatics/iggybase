from blinker import signal
import flask
from flask import current_app

from sqlalchemy import event
from sqlalchemy.engine import reflection
from flask_mail import Attachment, Connection, Message, Mail

"""# db_session and db should be passed to ActionManager when initiating.
# These imports are backups.
from database import db_session
from database import db
"""

event_registry = {}
act_manager = None

def db_event_pitcher(sender, **kw):
    """Dispatches databse events to be processed
    act_obj must have an execute method
    """
    sender.execute(**kw)


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

            key_combo = set([evt_cat, model_name, specific])
            registry_keys = set(event_registry.keys())
            outcomes = list(key_combo & registry_keys)

            for kk in outcomes:
                actions = event_registry.get(kk, None)

                # Shouldn't happen possible keys were anded with registry entries.
                if not actions:  
                    continue

            for action in actions:
                if action.verify(obj, evt_type):
                    action.dispatch(obj, event_type=evt_type)
    
    evt_cat = 'database'

    if session.deleted:
        print(session.deleted)
        evt_type = 'deleted'
        event_scan(session.deleted)
    if session.new:
        print(session.new)
        evt_type = 'new'
        event_scan(session.deleted)        
    if session.dirty:
        print(session.dirty)
        evt_type = 'dirty'
        event_scan(session.dirty)



def db_rollback(session):
    print('rolled back')


def init_app(app, session):
    app.act_manager = ActionManager(app, session)
    act_manager = app.act_manager
    return act_manager

    
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
        self.db_action_signal = signal('action_signal')
        self.db_action_signal.connect(db_event_pitcher)

        event.listen(self.session, 'before_flush', db_event)

        event.listen(self.session, 'after_rollback', db_rollback)

        
    def register_db_event(self, action):
        """Registers an action's event.

        The event is identified by category, name, and type. The 
        Categories are: database
        For database events:
             name is the __tablename__ of a SqlAlchemy model.
             event type is one of new|delete|dirty (changed)
        
        Wild cards are permitted for tablenames and event_types. 
        """
        valid_categories = ['database']
        valid_tablenames = reflection.Inspector.from_engine(self.session.get_bind()). \
                           get_table_names()
        valid_tablenames.append('*')
        valid_event_types = ['new', 'deleted', 'dirty', '*']

        # The registry is a flat dict by combining category and name.
        k = action.event_category
        if not k in valid_categories:
            raise ValueError( '%s is not a valid category %s' % \
                (k, str(valid_categories)))
        if action.event_name:
            if action.event_name not in valid_tablenames:
                raise ValueError( '%s is not a valid tablename %s' % \
                    (action.event_name, str(valid_tablenames)))
            k = k + ':' + action.event_name
        if action.event_type:
            if action.event_type not in valid_event_types:
                raise ValueError( '%s is not a valid event type %s, %s' % \
                    (action.event_type, k, str(valid_event_types)))
            k = k + ':' + action.event_type

        event_registry.setdefault(k, []).append(action)


    def unregister(self, action):
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
    For database events, names are the model name, and type is dirty, new, or deleted.

    default: database
    """
    name = 'Action'
    description = 'Base Action class for database events.'
    
    def __init__(self, cat='database', name=None, event_type=None, **kwargs):
        """
        verify_params (kwarg args)  are used by the verify method to further test the 
        validity of an event. They are passed as:
        tablename=xxx, fieldname=yyy, keyname=zzz, rows=[0....n]
        """
        self.event_category = cat if cat else ""
        self.event_name = name if cat and name else ""
        self.event_type = event_type if cat and name and event_type else ""
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


    def verify(self, obj, evt_type):
        """Validate event. 
        Returning False means the event is a don't care. 
        Otherwise, returning True (default)  validates the object.
        It can then be either call the execute method. Or, it can return True
        and the execute will be dispatched via a signal maybe in another thread.

        Override this method to further test the that the action should be
        executed.

        Old record values a passed as:
        tablename=tablename, fieldname=fieldname, keyname='id', rows=[0..n]
        """
        if hasattr(self, 'verify_object'):
            ret_val = self.verify_object.search_params(obj)
            if ret_val == 'changed':
                
                
                return True
            else:
                """
                probably log a info or something
                """
                return False


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
    


    def dispatch(self, obj, **kwargs):
        """Enqueue the object for a signal. 
        False return means nothing enqueued.
        """
        kwargs['obj'] = obj
        pitcher = signal('action_signal')
        print('sending signal with kwargs=%s' % (kwargs))
        pitcher.send(self, **kwargs)

    def execute(self, obj, **kwargs):
        "execute the action"
        return


class EmailAction(Action):

    log_mail = False

    def __init__(self, *args, **kwargs):
        """kwargs may contain email Message fields.

        If a message field is not provided as a parameter, that field's name, say - bcc, 
        can be derived by overidding the bcc method below or any one of the methods that
        corresponds to a Message field.

        Fields not now supported: html, extra_headers, mail_options, rcpt_options.
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
        body is a dict: 
            { 'text', template_data, 'context': { ... } }
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
        msg = Message(sender=current_app.config['DEFAULT_MAIL_SENDER'])
        for func in [getattr(self, aa) for aa in dir(self) if aa.startswith('get_')]:
            result = func()
            if result:
                head, sep, tail = func.__name__.partition('_')
                if tail == 'attachments':
                    for attachment in result:
                        msg.add_attachment(attachment)
                else:
                    setattr(msg, tail, result)

        import pdb
        pdb.set_trace()
        mail = Mail(current_app)
        mail.connect()
        mail.send(msg)
        if self.log_mail:
            """
            Log email to a table with a timestamp. Note, for attachements, don't only log the
            file name and content_type, not the data.
            """
        return

    def render_from_text(self, ctx):
        """
        ctx is { 'text', 'context': { ... } }
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
