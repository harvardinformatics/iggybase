from iggybase.admin.models import DatabaseEvent, EmailAction, ActionValue
from iggybase.utilities import get_table, get_func
from event_action import EmailAction, Action as EventAction



actions = []



class StartEvents(object):

    def __init__(self, app):
        self.app = app
        self.actions = []
        user = get_table('user')
        self.actions.append(EventAction(model=user, event_type='new'))

    def configure(self, db_session):
        """
        Look for events and register their actions.
        """
        """
        db_events = db_session.query(DatabaseEvent).filter_by(active=True)
        for db_event in db_events.all():
            actions = db_event.actions

            for act in actions:
                ctx = {}
                action_obj = EmailAction if act.action_type == 'email' else EventAction
                
                if act.action_type.name == 'email':
                    for action_val in act.action_values:
                        try:
                            query_obj = get_table(action_val.table_object.name)
                        except:
                            raise ValueError(' cannot load table %s' % table_object.name)
                        value = db_session.query(query_obj).first()
                        ctx[action_val.name] =  value

                    kwargs = {'body': {'text': act.text, 'context': ctx },
                              'subject': act.subject,
                              'email_recipients': act.email_recipients}

                    if act.email_cc:
                        kwargs['cc'] = act.email_cc
                    if act.email_bcc:
                        kwargs['bcc'] = act.email_cc

                verify_callback = get_func(action_obj.callback_func_module,
                                           action_obj.verify_callback_func)
                
                execute_callback = get_func(action_obj.callback_func_module,
                                            action_obj.execute_callback_func)
                    
                new_action = action_obj(get_table(db_event.table_object.name),
                                        db_event.field.display_name,
                                        db_event.event_type.name,
                                        verify_callback = verify_callback,
                                        execute_callback = execute_callback,
                                        **kwargs)
                self.actions.append(new_action)

        for action in self.actions:
            self.app.act_manager.register_db_event(action)
        """
        return
