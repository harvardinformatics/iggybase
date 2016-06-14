from flask import abort, g
from iggybase import utilities as util
from iggybase.core.field_collection import FieldCollection
from iggybase import g_helper
import random
import datetime
import logging

class DataInstance:
    def __init__(self, table_name, instance_name = 'new', instance_id = None):
        self.organization_access_control = g_helper.get_org_access_control()
        role_access_control = g_helper.get_role_access_control()

        self.table_data = role_access_control.has_access('TableObject', {'name': table_name})
        if self.table_data is None:
            abort(403)

        self.table_name = table_name
        self.instance_name = instance_name
        self.table_object = util.get_table(table_name)

        self.instance = self.get_instance(instance_name, instance_id)

        if self.instance.name is None or instance_name == 'new':
            self.instance_name = self.set_instance_name()
            self.new = True
        else:
            self.new = False
            self.instance_name = instance_name

        self.fields, self.field_values, self.original_values = self.initialize_field_values()

        self.history = []

    def get_instance(self, instance_name, instance_id = None):
        if instance_id is None:
            instance = self.organization_access_control.get_instance_data(self.table_object,
                                                                               {'name': instance_name})
        else:
            instance = self.organization_access_control.get_instance_data(self.table_object,
                                                                               {'id': instance_id})
        return instance

    def initialize_field_values(self):
        field_collection = FieldCollection(None, self.table_name)

        fields = {}
        field_values = {}
        orig_values = {}
        field_collection.set_defaults()

        for field, meta_data in field_collection.fields.items():
            fields[meta_data.Field.display_name] = meta_data
            if self.new and meta_data.default is not None:
                field_values[meta_data.Field.display_name] = meta_data.default
                orig_values[meta_data.Field.display_name] = meta_data.default
            elif self.new:
                field_values[meta_data.Field.display_name] = None
                orig_values[meta_data.Field.display_name] = None
            else:
                field_values[meta_data.Field.display_name] = getattr(self.instance, meta_data.Field.display_name)
                orig_values[meta_data.Field.display_name] = getattr(self.instance, meta_data.Field.display_name)

        return fields, field_values, orig_values

    def update_field_values(self):
        for name, value in self.field_values.items():
            self.field_values[name] = getattr(self.instance, name)
            self.original_values[name] = getattr(self.instance, name)

    def set_value(self, field_name, field_value):
        self.field_values[field_name] = field_value

        if field_name == 'name':
            self.instance_name = field_value

    def set_values(self, field_values = {}):
        for field_name, field_value in field_values.items():
            self.field_values[field_name] = field_value

        if 'name' in field_values.keys():
            self.instance_name = field_values['name']

    def set_foreign_key_field_id(self, text_values = {}):
        role_access_control = g_helper.get_role_access_control()

        id_values = []
        for field, value in text_values.items():
            if self.fields[field].Field.foreign_key_display is None:
                fk_field_display = 'name'
            else:
                fk_field_data = role_access_control.fields(self.fields[field].Field.foreign_key_table_object_id,
                                                           {'field.id': self.fields[field].Field.foreign_key_display})

                fk_field_display = fk_field_data.Field.name

            fk_table_data = role_access_control.has_access('TableObject',
                                                           {'id': self.fields[field].Field.foreign_key_table_object_id})

            fk_table_object = util.get_table(fk_table_data.name)

            fk_id = self.organization_access_control.session.query(fk_table_object). \
                filter(getattr(fk_table_object, fk_field_display) == value).first()

            if fk_id:
                id_values.append(fk_id.id)
                self.field_values[field] = fk_id.id
            else:
                id_values.append(None)
                self.field_values[field] = None

        return id_values

    def get_value(self, field_name):
        return self.field_values[field_name]

    def get_values(self):
        return self.field_values

    def save(self):
        if self.new or self.instance.get_value('date_created') is None:
            self.set_value('date_created', datetime.datetime.utcnow())

        self.set_value('last_modified', datetime.datetime.utcnow())
        self.set_value('name', self.instance_name)

        for field_name, value in self.field_values.items():
            setattr(self.instance, field_name, value)

        if self.table_name != 'history':
            self.changed_values()
            for history in self.history:
                history_instance = DataInstance('history')
                history_instance.set_values(history)
                history_instance.save()

        save_msg = self.organization_access_control.save_data_instance(self.instance)

        self.new = False

        self.instance = self.get_instance(save_msg['name'])

        self.fields, self.field_values, self.original_values = self.initialize_field_values()

        logging.info('id at save post-refresh: ')
        logging.info(self.instance.id)

        logging.info('name at save: ' )
        logging.info(self.instance.name)

        return save_msg

    def set_instance_name(self):
        if self.table_data.new_name_prefix is not None and self.table_data.new_name_prefix != "":
            instance_name = self.organization_access_control.get_new_name(self.table_name)
        else:
            instance_name = self.table_name + str(random.randint(1000000000, 9999999999))

        # logging.info('name at set_instance_name: ' + instance_name)

        return instance_name

    def changed_values(self):
        exclude_list = ['date_created', 'last_modified']
        for name, value in self.original_values.items():
            # logging.info('name orig: ' + name)
            # logging.info('value orig: ' + str(value))
            # logging.info('value new: ' + str(self.field_values[name]))

            if not ((value is None and self.field_values[name] is None) or (value == self.field_values[name])) and \
                                        name not in exclude_list:
                self.history.append({'table_object_id': self.table_data.id,
                                     'field_id': self.fields[name].Field.id,
                                     'organization_id': self.instance.organization_id,
                                     'instance_name': self.instance_name,
                                     'old_value': value, 'user_id': g.user.id,
                                     'new_value': self.field_values[name]})
