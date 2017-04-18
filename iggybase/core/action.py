from iggybase import g_helper
from flask.ext.mail import Message
from iggybase.extensions import mail
from importlib import import_module
from iggybase.core.constants import ActionType, timing
from re import split, findall
from json import loads
from collections import OrderedDict
import logging


class Action:
    def __init__(self, action_type=None, action_target=None):
        self.oac = g_helper.get_org_access_control()
        self.results = None
        self.actions = {}
        self.action_type = action_type
        if action_type == ActionType.STEP and action_target is not None:
            self.set_step_actions(action_target)
        elif action_type == ActionType.TABLE and action_target is not None:
            self.set_table_object_actions(action_target)

    def set_step_actions(self, step_id, active=1):
        self.action_type = ActionType.STEP
        self.actions[timing.BEFORE] = OrderedDict()
        self.actions[timing.AFTER] = OrderedDict()

        actions = self.oac.get_step_actions(step_id, timing.BEFORE, active)
        for action in actions:
            self.actions[timing.BEFORE][action.Action.name] = action

        actions = self.oac.get_step_actions(step_id, timing.AFTER, active)
        for action in actions:
            self.actions[timing.AFTER][action.Action.name] = action

    def set_table_object_actions(self, table_object_name, active=1):
        self.action_type = ActionType.TABLE
        self.actions['insert'] = OrderedDict()
        self.actions['update'] = OrderedDict()

        actions = self.oac.get_table_object_actions(table_object_name, 'insert', active)
        for action in actions:
            self.actions['insert'][action.Action.name] = action

        actions = self.oac.get_table_object_actions(table_object_name, 'update', active)
        for action in actions:
            self.actions['update'][action.Action.name] = action

    def send_mail(self, action_email, **kwargs):
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

        send_to = {'recipitents': action_email.recipitents, 'cc': action_email.cc, 'bcc': action_email}

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

            msg = Message(action_email.subject)

            if index < len(attachments):
                attachment = attachments[index]
            else:
                attachment = attachments[0]

            if attachment is not None:
                msg.attachments = attachment

        mail.send(msg)

    def execute_action(self, event, **kwargs):
        action_status = False

        for action_name, action_data in self.actions[event].items():
            logging.info(action_name)
            action_kwargs = {}
            parameter_not_found = False

            if action_data.Action.variable_parameters:
                parameters = split(', |,|;|; ', action_data.Action.variable_parameters)
                logging.info(parameters)
                for parameter in parameters:
                    if parameter in kwargs:
                        logging.info('parameter found: ' + parameter)
                        action_kwargs[parameter] = kwargs[parameter]
                    else:
                        logging.info('parameter not found: ' + parameter)
                        parameter_not_found = True

            if action_data.Action.fixed_parameters:
                action_kwargs.update(loads(action_data.Action.fixed_parameters))

            if self.action_type == ActionType.TABLE and action_data.Action.field_id:
                action_kwargs['field_id'] = action_data.Action.field_id
                action_kwargs['field_value'] = action_data.Action.field_value

            if action_data.Action.namespace and action_data.Action.function and not parameter_not_found:

                logging.info(self.actions[event][action_name].Action.namespace)
                logging.info(self.actions[event][action_name].Action.function)
                action_module = import_module(self.actions[event][action_name].Action.namespace)
                action_method = getattr(action_module, self.actions[event][action_name].Action.function)

                logging.info('**action_kwargs')
                logging.info(action_kwargs)
                action_status, self.results = action_method(**action_kwargs)

            if self.actions[event][action_name].ActionEmail and not parameter_not_found:
                self.send_mail(self.actions[event][action_name].ActionEmail, **action_kwargs)

        return action_status
