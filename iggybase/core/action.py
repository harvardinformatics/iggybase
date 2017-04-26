from iggybase import g_helper
from flask.ext.mail import Message
from iggybase.extensions import mail
from importlib import import_module
from iggybase.core.constants import ActionType, Timing, DatabaseEvent
from re import split, findall
from json import loads
import logging


class Action:
    def __init__(self, action_type, **kwargs):
        self.oac = g_helper.get_org_access_control()
        self.results = None
        self.action = None
        self.action_type = None
        if action_type == ActionType.STEP and 'action_step' in kwargs and 'action_timing' in kwargs:
            self.set_step_actions(kwargs['action_step'], kwargs['action_timing'])
        elif action_type == ActionType.TABLE and 'action_table' in kwargs and 'action_event' in kwargs:
            self.set_table_object_actions(kwargs['action_table'], kwargs['action_event'])
        elif action_type == ActionType.ACTION_SUMMARY and 'action_name' in kwargs:
            self.set_table_object_actions(kwargs['action_name'])

    def set_action(self, action_name, active=1):
        self.action_type = ActionType.ACTION_SUMMARY

        self.action = self.oac.get_action(action_name, active)

    def set_step_actions(self, step_id, step_timing, active=1):
        self.action_type = ActionType.STEP

        self.action = self.oac.get_step_actions(step_id, step_timing, active)

    def set_table_object_actions(self, table_object_name, step_event, active=1):
        self.action_type = ActionType.TABLE

        self.action = self.oac.get_table_object_actions(table_object_name, step_event, active)

    def send_mail(self, *args, **kwargs):
        if 'instances' in kwargs.keys():
            instances = kwargs['instances']
        elif 'instance' in kwargs.keys():
            instances = [kwargs['instance']]
        else:
            instances = [None]

        if 'attachments' in kwargs.keys():
            attachments = kwargs['attachments']
        elif 'attachment' in kwargs.keys():
            attachments = [kwargs['attachment']]
        else:
            attachments = [None]

        rac = g_helper.get_role_access_control()

        send_to = {'recipitents': args[0].recipitents, 'cc': args[0].cc, 'bcc': args[0].bcc}

        for index, instance in enumerate(instances):
            for key, value in send_to.items():
                if value is None or value == '':
                    continue

                positions = findall('\<.*\>', value)
                for position in positions:
                    if instance is None:
                        # uses self.oac.current_org_id
                        client_position_users = self.oac.get_users_by_position(position)
                    else:
                        client_position_users = self.oac.get_users_by_position(instance.organization_id)

                    facility_position_users = self.oac.get_users_by_position(position,
                                                                             rac.facility.root_organization_id)
                    position_email = ' '
                    for user in client_position_users:
                        position_email += user.User.email + ';'
                    for user in facility_position_users:
                        position_email += user.User.email + ';'

                    value.replace('<' + position + '>', position_email[:-1].strip())

                send_to[key] = split(', |,| |;|; ', value)

            msg = Message(args[0].subject)
            msg.body = args[0].body

            if index < len(attachments):
                attachment = attachments[index]
            else:
                attachment = attachments[0]

            if attachment is not None:
                msg.attachments = attachment

        mail.send(msg)

    def execute_action(self, *args, **kwargs):
        action_status = False

        action_kwargs = {}
        parameter_not_found = False

        if self.action.Action.variable_parameters:
            parameters = split(', |,|;|; ', self.action.Action.variable_parameters)
            for parameter in parameters:
                if parameter in kwargs:
                    action_kwargs[parameter] = kwargs[parameter]
                else:
                    parameter_not_found = True

        if self.action.Action.fixed_parameters:
            action_kwargs.update(loads(self.action.Action.fixed_parameters))

        if self.action_type == ActionType.TABLE and self.action.Action.field_id:
            action_kwargs['field_id'] = self.action.Action.field_id
            action_kwargs['field_value'] = self.action.Action.field_value

        if self.action.Action.namespace and self.action.Action.function and not parameter_not_found:

            action_module = import_module(self.action.Action.namespace)
            action_method = getattr(action_module, self.action.Action.function)

            action_status, self.results = action_method(*args, **action_kwargs)

        if self.action.ActionEmail and not parameter_not_found:
            self.send_mail(self.action.ActionEmail, **action_kwargs)

        return action_status
