from blinker import signal
import flask
from flask import current_app

from sqlalchemy import event
from sqlalchemy.engine import reflection


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
    if obj:
        obj.execute(obj, kw)
    else:
        print('no object named obj')


def db_event(session, stat, instances):
    """Dispatcher for database events
    """

    def event_scan(session_itr):
        """Scans the event objects (db table create/update/delete actions).
        """
        
        for obj in session_itr:
            evt_name =  obj.__tablename__
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
        self.verify_params = {}
        if kwargs:
            for k,v in kwargs.items():
                setattr(self, k, v)


    def load_params(tablename, fieldname, keyname, rows):
        """
        Load db rows into a searchable set of nested dicts:
            { 'tablename': { 'fieldname' : { 'id': value }, ... }, ... }
        """
        table_level = self.verify_params.setdefault(tablename, {})
        name_level = table_level.set_default(fieldname, {})
        for row in rows:
            if row.has_key(keyname):
                print('Error adding value %s from row with key %s to table %s' \
                            % (fieldname, keyname, tablename))
            name_level[keyname] = getattr(row, fieldname, None)



    def add_param(tablename, fieldname, keyname, row):
        """Add a new entry to the verifiable params
        """
        self.load_params(tablename, fieldname, keyname, [row])


    def delete_param(tablename, fieldname, keyname):
                      
        try:
            table_level = self.verify_params[tablename]
            name_level = table_level[fieldname]
            name_level.pop(keyname)
            if len(name_level) == 0:
                table_level.pop(fieldname)
            if len(table_level) == 0:
                self.verify_params.pop(tablename)

        except KeyError:
            print('Error deleting value %s from row with key %s from table %s' \
                  % (fieldname, keyname, tablename))
            return

    def update_param(tablename, fieldname, keyname, newval):
        try:
            table_level = self.verify_params[tablename]
            name_level = table_level[fieldname]
            name_level[keyname] = newval

        except KeyError:
            print('Error updating value %s in row with key %s, table %s' \
                               % (fieldname, keyname, tablename))
            return


    def search_params(obj):
        tablename = obj.__tablename__
        table_level = self.verify_params[tablename]
        names = table_level.keys()
        if names:
            for name in names:
                name_level = table_level[name]
                keyname = obj.id
                if name_level.has_key(keyname):
                    value = name_level[keynsma]
                    if value == getattr(obj, keyname, None):
                        return 'unchanged'
                    else:
                        return 'changed'
        return 'not_found'
                


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
        if self.kwargs:
            for k,v in kwargs.items():
                setattr(self, k, v)
        self.tablename = getattr(self, 'tablename', None)
        self.fieldname = getattr(self, 'fieldname', None)
        self.keyname = getattr(self, 'keyname', None)
        self.rows = getattr(self, 'rows', None)
        if self.tablename and self.fieldname and self.keyname and self.rows:
            self.verify_params = VerifyObject()
            self.verify_params.load_params(tablename, fieldname, keyname, rows)


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
        import pdb
        pdb.set_trace()
        if hasattr(self, verify_params):
            ret_val = self.verify_params.search_params(obj)
            if ret_val == 'changed':
                return True
            else:
                """
                probably log a info or something
                """
                return False


    def load_params(tablename=None, fieldname=None, keyname=None, rows=None):
        """Load parameters to verify.
        The verify parameters may also be loaded when initiating the Action object.
        """
        if tablename and fieldname and keyname and rows:
            self.verify_params = VerifyObject()
            self.verify_params.load_params(tablename, fieldname, keyname, rows)
        else:
            raise ValueError('Missing params')
        return
    


    def dispatch(self, obj, **kwargs):
        """Enqueue the object for a signal. 
        False return means nothing enqueued.
        """
        pitcher = signal('action_signal')
        print('sending signal with kwargs=%s' % (kwargs))
        pitcher.send(self, kwargs)

    def execute(self, obj, *kwargs):
        "execute the action"
        return


class EmailAction(Action):
    from flask_mail import Attachment, Connection, Message, Mail

    log_mail = False

    def __init__(self, *args, **kwargs):
        """kwargs may contain email Message fields.

        If a field is not provided as a parameter, that field's name, say - bcc, can
        be derived by overidding the bcc method below or any one of the methods that
        corresponds to a Message field.

        Fields not now supported: html, extra_headers, mail_options, rcpt_options.
        """
        Action.__init__(self, *args, **kwargs)

        
    def subject(self, **kwargs):
        """
        Email subject string.
        Override to provide object's subject
        """
        if hasattr(self, 'subject'):
            return getattr(self, 'subject', None)
        return None
    
    def recipients(self, **kwargs):
        """
        Recipients list
        """
        if hasattr(self, 'recipients'):
            return getattr(self, 'recipients', None)
        return None

    def cc(self, **kwargs):
        if hasattr(self, cc.__name__):
            return getattr(self, cc.__name__, None)
        return None

    def bcc(self, **kwargs):
        if hasattr(self, bcc.__name__):
            return getattr(self, bcc.__name__, None)
        return None

    def body(self, **kwargs):
        """
        body is a dict: 
            { 'text', template_data, 'context': { ... } }
        """
        if hasattr(self, body.__name__):
            return render(getattr(self, body.__name__, None))
        return None

    def attachments(self, **kwargs):
        """
        Attachment list expects a list of dicts with:
            filename=filename,
            content_type=content_type,  (mime_type)
            data=data,
        """
        attchs = []
        if hasattr(self, attachments.__name__):
            for attach in getattr(self, attachments.__name__):
                attchs.append(Attach(attach))
            return attchs
        return None

        
    def reply_to(self, **kwargs):
        if hasattr(self, reply_to.__name__):
            return getattr(self, reply_to.__name__, None)
        return None

    def charset(self, **kwargs):
        if hasattr(self, charset.__name__, None):
            return getattr(self, charset.__name__, None)
        return None


    def execute(self, **kwargs):
        """
        Send email message
        """
        msg_args = {}
        for func in [subject, recipients, cc, bcc, body,
                     attachments, reply_to, charset]:
            result = func()
            if result:
                msg_args[func.__name__] = result
        
        mail = Mail()
        # mail might already be initialized??
        mail.init_app(current_app)
        mail.send_message(**msg_args)

        if log_mail:
            """
            Log email to a table with a timestamp. Note, for attachements, don't only log the
            file name and content_type, not the data.
            """
            return

    def render_from_text(self, ctx, environ=None):
        """
        ctx is { 'text', data, 'context': { ... } }
        """
        env = environ if environ else Environment()
        template = env.from_string(ctx['text'])
        return template.render(ctx['context'])
    

    def render_from_template(self, ctx, environ):
        """
        Mail environment must be valid in order to find the 
        template in the file system.
        ctx is { 'template': xxx.html, 'context': { ... } }
        """
        template = environ.get_templagte(ctx['template'])
        return template.render(ctx['context'])
