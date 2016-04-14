from iggybase.admin.models import DatabaseEvent, EmailAction, ActionValue
from event_action import EmailAction

class StartEvents(object):
    actions = []

    def configure(self, db_session):
        """
        Look for events and register their actions.
        """
        db_events = db_session.query(DatabaseEvent).filter_by(active=True)
        for db_event in db_events:
            actions = db_event.action
            ctx = {}
            for act in actions:
                if act.name == 'email':
                    for val in action_value:
                        value = query(table_object.name.__class__.field.name).first()
                        ctx[val.name] =  value
                        kwargs = {'text': act.text,
                                  'ctx': ctx,
                                  'subject': act.subject,
                                  'email_recipients': act.email_recipients}

                        if act.email_cc:
                            kwargs['cc'] = act.email_cc
                        if act.email_bcc:
                            kwargs['bcc'] = act.email_cc

                        e_action = EmailAction(db_event.table_object.name,
                                               db_event.field.field_name,
                                               db_event.event_type.name,
                                               **kwargs)
                        actions.append(e_action)
            
                                   
        
