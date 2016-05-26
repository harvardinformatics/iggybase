from iggybase.admin.models import DatabaseEvent, EmailAction, Action
from iggybase.utilities import get_table, get_func
from event_action import EmailAction, Action as EventAction
from iggybase.admin.models import User
import logging


my_actions = []

class StartEvents(object):

    def __init__(self, app):
        self.app = app

    def configure(self, db_session):
        
        """
        Look for events and register their actions.
        """
        my_actions.append(NewUserNotify())
        my_actions.append(UserEmailChange())

        for new_action in my_actions:
            self.app.act_manager.register_db_event(new_action)

                                   
        
class NewUserNotify(EmailAction):
    name = 'NewUserNotify'

    model = User
    field_name = None
    event_type = 'new'

    subject = 'New User Created'
    recipients = ['reuven@koblick.com',]

    body = {'text': """A new user {{ username }} was created.""" } 


    def get_body(self, **kwargs):
        self.body['context'] = {'username': kwargs['obj'].name}
        return self.render_from_text(self.body)


class UserEmailChange(EmailAction):
    name = 'ChangedEmailAddress'

    model = User
    field_name = 'email'
    event_type = 'dirty'
    text = '{{ username  }} changed email address from {{ oldvalue }} to {{ newvalue}}'

    subject = 'Changed Email Address'
    recipients = ['reuven@koblick.com']

    def get_body(self, **kwargs):
        self.body = {'text': self.text,
                     'context': {'oldvalue': kwargs['oldvalue'] ,
                                 'newvalue': kwargs['newvalue'],
                                 'username': kwargs['obj'].name, }
        }
        return self.render_from_text(self.body)



