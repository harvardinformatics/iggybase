from iggybase.admin.models import DatabaseEvent, EmailAction, ActionValue
from iggybase.utilities import get_table
from event_action import EmailAction

class StartEvents(object):
    actions = []

    def configure(self, db_session):
        """
        Look for events and register their actions.
        """
        db_events = db_session.query(DatabaseEvent).filter_by(active=True)
        for db_event in db_events.all():
            actions = db_event.actions
            ctx = {}
            for act in actions:
                if act.action_type.name == 'email':
                    for action_val in action_values:
                        try:
                            table = action_valget_table(table_object.name)
                            query_obj = getattr(table, action_val.field.name)
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

                    e_action = EmailAction(db_event.table_object.name,
                                           db_event.field.display_name,
                                           db_event.event_type.name,
                                           **kwargs)
                    actions.append(e_action)

                                   
        
