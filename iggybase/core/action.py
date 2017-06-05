from iggybase import g_helper
from flask.ext.mail import Message
from iggybase.extensions import mail
from importlib import import_module
from iggybase.core.constants import ActionType
from iggybase.core.compare import Compare
from re import split, findall
from json import loads
import logging


class Action:
    def __init__(self, action_type, **kwargs):
        self.oac = g_helper.get_org_access_control()
        self.results = {}
        self.actions = None
        self.current_action = None
        self.action_type = None
        if action_type == ActionType.STEP and 'action_step' in kwargs and 'action_timing' in kwargs:
            self.set_step_actions(kwargs['action_step'], kwargs['action_timing'])
        elif action_type == ActionType.TABLE and 'action_table' in kwargs and 'action_event' in kwargs:
            self.set_table_object_actions(kwargs['action_table'], kwargs['action_event'])
        elif action_type == ActionType.ACTION_SUMMARY and 'action_name' in kwargs:
            self.set_table_object_actions(kwargs['action_name'])

    def set_action(self, action_name, active=1):
        self.action_type = ActionType.ACTION_SUMMARY

        self.current_action = self.oac.get_action(action_name, active)

    def set_step_actions(self, step_id, step_timing, active=1):
        self.action_type = ActionType.STEP

        self.current_action = self.oac.get_step_actions(step_id, step_timing, active)

    def set_table_object_actions(self, table_object_name, table_event, active=1):
        self.action_type = ActionType.TABLE

        self.actions = self.oac.get_table_object_actions(table_object_name, table_event, active)

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
        expected_values = ['status']
        parameter_not_found = False
        return_values = {}

        if self.current_action.Action.fixed_parameters:
            kwargs.update(loads(self.current_action.Action.fixed_parameters))

        if self.current_action.Action.namespace and self.current_action.Action.function and not parameter_not_found:
            action_module = import_module(self.current_action.Action.namespace)
            action_method = getattr(action_module, self.current_action.Action.function)

            return_values = action_method(*args, **kwargs)

        if self.current_action.ActionEmail and not parameter_not_found:
            self.send_mail(self.current_action.ActionEmail, **kwargs)

        temp_values = {}
        if self.current_action.Action.return_values and 'status' in return_values.keys() and return_values['status']:
            expected_values += split(', |,|;|; ', self.current_action.Action.return_values)
            for value in expected_values:
                if value in return_values.keys() and return_values['status']:
                    temp_values[value] = return_values[value]
                else:
                    if return_values['status']:
                        temp_values = {}
                        return_values['status'] = False

                    temp_values[value] = 'Action return value ' + value + ' was not found.'
        elif self.current_action.Action.return_values and 'status' not in return_values.keys():
            temp_values['status'] = False
            temp_values['error'] = 'Status was not returned from function'

        self.results.update(temp_values)

        return self.results['status']

    def execute_table_actions(self, table_id, modified_columns, instance_id, **kwargs):
        status = None

        if self.actions is not None:
            for action in self.actions:
                self.current_action = action
                if action.ActionTableObject.field_id is None:
                    status = action.execute_action(table_id=table_id,
                                                   field_id=None,
                                                   values=None,
                                                   instance_id=instance_id,
                                                   **kwargs)
                elif action.ActionTableObject.field_id in modified_columns.keys() and \
                                action.ActionTableObject.field_value and action.ActionTableObject.field_value != '':
                    if Compare.evaluate_value(action.Action.field_value,
                                              modified_columns[action.ActionTableObject.field_id][1]):
                        status = action.execute_action(table_id=table_id,
                                                       field_id=action.ActionTableObject.field_id,
                                                       values=modified_columns[action.ActionTableObject.field_id],
                                                       instance_id=instance_id,
                                                       **kwargs)

        return status
