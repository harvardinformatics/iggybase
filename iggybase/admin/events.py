from iggybase.admin.models import DatabaseEvent, EmailAction, Action
from iggybase.utilities import get_table, get_func
from event_action import EmailAction, Action as EventAction
import logging


my_actions = []

class StartEvents(object):

    def __init__(self, app):
        self.app = app

    def configure(self, db_session):
        """
        Look for events and register their actions.
        """
        db_events = db_session.query(DatabaseEvent).filter_by(active=True)
        for db_event in db_events.all():
            actions = db_event.actions
            try:
                for act in actions:
                    ctx = {}
                    kwargs = {}
                    action_obj = EventAction
                    if act.action_type.name == 'email':
                        action_obj = EmailAction
                        for action_val in act.action_values:
                            try:
                                query_obj = get_table(action_val.table_object.name)
                            except:
                                raise ValueError(' cannot load table %s' % table_object.name)
                            value = db_session.query(query_obj).first()
                            ctx[action_val.name] =  value

                        kwargs.update({'body': {'text': act.text, 'context': ctx },
                                  'subject': act.subject,
                                  'email_recipients': act.email_recipients})

                        if act.email_cc:
                            kwargs['cc'] = act.email_cc
                        if act.email_bcc:
                            kwargs['bcc'] = act.email_cc

                    verify_callback = None if not act.callback_func_module or \
                                      not act.verify_callback_func else \
                                      get_func(act.callback_func_module,
                                               act.verify_callback_func)

                    execute_callback = None if not act.callback_func_module or \
                                      not act.execute_callback_func else \
                                      get_func(act.callback_func_module,
                                               act.execute_callback_func)

                    dbe_field = db_event.field if hasattr(db_event, 'field') else None
                    display_name = None if dbe_field == None else dbe_field.display_name

                    new_action = action_obj(model=get_table(db_event.table_object.name),
                                            display_name=display_name,
                                            event_type=db_event.event_type.name,
                                            verify_callback=verify_callback,
                                            execute_callback=execute_callback, **kwargs)

                    my_actions.append(new_action)                
            except:
                logging.error('an error occured configuring event', act)
                db_session.rollback()   # just in case.


        for new_action in my_actions:
            self.app.act_manager.register_db_event(new_action)

                                   
        
