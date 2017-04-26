from flask import abort, g
from iggybase.core.table_collection import TableCollection
from iggybase.core.instance_data import InstanceData
from iggybase import g_helper
from collections import OrderedDict
from datetime import datetime
from iggybase.core.action import Action
import logging


class InstanceCollection:
    def __init__(self, depth = 2, instance_data=None):
        if instance_data is None:
            instance_data = {}
        elif not isinstance(instance_data, dict):
            raise TypeError('instance_data should be dictionary containing {table name: [instance name]}')

        self.rac = g_helper.get_role_access_control()
        self.oac = g_helper.get_org_access_control()

        self.background_save_instances = {}
        self.base_instance = None
        self.instance_counter = 1
        self.instances = OrderedDict()
        self.table_instances = OrderedDict()
        self.instance_names = {}

        self.tables = TableCollection(instance_data.keys(), depth)

        for table_name in self.tables.table_names:
            self.table_instances[table_name] = {}
            self.instance_names[table_name] = {}


        for table_name, instance_names in instance_data.items():
            if instance_names:
                if isinstance(instance_names, str):
                    self.get_data(table_name, {'name': [instance_names]})
                else:
                    self.get_data(table_name, {'name': instance_names})

    @property
    def instance(self):
        return self.base_instance

    def __iter__(self):
        return iter(self.instances)

    def __getitem__(self, instance_name):
        return self.instances[instance_name]

    def keys(self):
        return self.instances.keys()

    def items(self):
        return self.instances.items()

    def values(self):
        return self.instances.values()

    def set_instances(self, instances=[]):
        instances_names = []
        
        for row in instances:
            instance = InstanceData(row, row.name, self.instance_counter)

            if instance.new_instance:
                if instance.table_name not in self.tables.keys():
                    self.tables.add_table(instance.table_name)
                    logging.info('set_instances new table: ' + instance.table_name)
                logging.info('set_instances initialize values: ' + instance.table_name)
                instance.initialize_values(self.tables[instance.table_name].fields)

            if self.base_instance is None:
                self.base_instance = instance

            self.instances[instance.instance_name] = instance
            self.table_instances[instance.table_name][instance.instance_name] = instance

            instances_names.append(instance.instance_name)
            
            self.instance_names[instance.table_name][instance.instance_name] = instance.instance_name
            self.instance_counter += 1
            
        return instances_names

    def get_data(self, table_name, instance_dict):
        instances_names = []

        instances = self.oac.get_instance_data(self.tables[table_name].table_instance, instance_dict)

        tmp_instances_names = self.set_instances(instances)

        instances_names += tmp_instances_names

        return instances_names

    def add_new_instances(self, table_name, quantity=0):
        instance_names = []

        i = 0
        while i < quantity:
            instance_names.append(self.add_instance(table_name))
            i += 1

        return instance_names

    def add_instance(self, table_name, instance_name=None):
        if instance_name is None:
            instance_name = {'name': ['new']}

        instance_name = self.get_data(table_name, instance_name)

        return instance_name[0]

    def get_linked_instances(self, root_id):
        for table_name, table_data in self.tables.items():
            if table_data.level == 1:
                ids = [root_id]

            if table_data.link_type == "child":
                child_rows = self.oac.get_descendant_data(table_name, table_data.link_data.child_link_field_id, ids)

                ids = []

                if child_rows:
                    for row in child_rows:
                        instance_names = self.set_instances([row['instance']])
                        self.instances[instance_names[0]].set_parent_id(table_data.parent_link_field_display_name,
                                                                        row['parent_id'])
                        ids.append(row['instance'].id)
                else:
                    instance_names = self.get_data(table_name, {'name': ['empty_row']})
                    if table_data.level == 1:
                        self.instances[instance_names[0]].set_parent_id(table_data.parent_link_field_display_name,
                                                                        root_id)
            elif table_data.link_type == "many":
                pass
            elif table_data.link_type == "table_id":
                pass

    def set_values(self, instance_name, field_values = {}):
        for field_name, field_value in field_values.items():
            self.set_value(instance_name, field_name, field_value)

    def set_value(self, instance_name, field_name, field_value):
        exclude_list = ['id', 'last_modified', 'date_created']

        table_name = self.instances[instance_name].table_name
        field = self.tables[table_name].fields[table_name + "|" + field_name]
        instance = self.instances[instance_name].instance
        instance_value = getattr(instance, field_name)

        if field.is_foreign_key and field_value is not None:
            field_value = self.instances[instance_name].set_foreign_key_field(self.tables[table_name].table_object.id,
                                                                              field,
                                                                              field_value)
        if field.type == 'boolean':
            instance_value = bool(instance_value)

        if table_name == 'history' :
            setattr(self.instances[instance_name].instance, field_name, field_value)
        elif (field_name not in exclude_list and
                ((instance_value is None and field_value is not None) or
                 (instance_value is not None and field_value is None) or field_value != instance_value) and
                ((not (field_name == 'name' and field_value is None and self.instances[instance_name].new_instance) and
                  self.tables[table_name].level == 0) or (field_name != 'name'))):

            # logging.info('table_name: ' + table_name + '    field_name: ' + field_name + "   field_value: " +
            #              str(field_value) + " type: " +
            #              str(type(field_value)) + "   getattr: " +
            #              str(instance_value) + " type: " +
            #              str(type(instance_value)))
            # logging.info('self.instances[instance_name].new_instance: ' +
            #              str(self.instances[instance_name].new_instance))
            # logging.info('field_name not in exclude_list: ' + str(field_name not in exclude_list))
            # logging.info('(instance_value is None and field_value is not None): ' + str(
            #     (instance_value is None and field_value is not None)))
            # logging.info('(instance_value is not None and field_value is None): ' + str(
            #     (instance_value is not None and field_value is None)))
            # logging.info('field_value != instance_value: ' + str(field_value != instance_value))
            # logging.info('not (field_name == name and field_value is None and ' \
            #              'self.instances[instance_name].new_instance): ' + \
            #              str(not (field_name == 'name' and field_value is None and
            #                       self.instances[instance_name].new_instance)))
            # logging.info('self.tables[table_name].level == 0: ' + str(self.tables[table_name].level == 0))
            # logging.info('saving data')
            # logging.info('')

            self.instances[instance_name].save = True
            new_key = self.add_instance('history')

            self.set_values(new_key,
                            {'table_object_id': self.tables[table_name].table_object.id,
                             'field_id': field.Field.id,
                             'organization_id':  getattr(instance, 'organization_id'),
                             'instance_name': instance_name,
                             'old_value': getattr(instance, field_name, None),
                             'user_id': g.user.id,
                             'new_value': field_value})

            setattr(self.instances[instance_name].instance, field_name, field_value)

    def commit(self):
        inst_names = {}
        instances = []
        actions = {}

        for instance_name in self.instances.keys():
            if not self.instances[instance_name].save or self.instances[instance_name].table_name == 'history':
                continue

            if self.instances[instance_name].instance.date_created is None:
                self.instances[instance_name].instance.date_created = datetime.utcnow()

            self.instances[instance_name].instance.last_modified = datetime.utcnow()

            if self.instances[instance_name].new_instance:
                if self.instances[instance_name].instance.name is None or \
                                self.instances[instance_name].instance.name == '' or \
                                'new' in self.instances[instance_name].instance.name or \
                                'empty_row' in self.instances[instance_name].instance.name:
                    new_name = self.tables[self.instances[instance_name].table_name].table_object.get_new_name()
                    self.instances[instance_name].set_name(new_name)
                    self.background_save_instances[self.instances[instance_name].table_name] = \
                        self.tables[self.instances[instance_name].table_name].table_object
                else:
                    self.instances[instance_name].set_name(self.instances[instance_name].name)

                instances.append(self.instances[instance_name].instance)
            else:
                instances.append(self.instances[instance_name].instance)

            self.instance_names[self.instances[instance_name].table_name][self.instances[instance_name].old_name] = \
                self.instances[instance_name].instance_name
            inst_names[self.instances[instance_name].old_name] = self.instances[instance_name].instance_name

        for history_name in self.table_instances['history'].keys():
            if self.instances[history_name].instance.instance_name in inst_names.keys():
                self.instances[history_name].instance.instance_name = \
                    inst_names[self.instances[history_name].instance.instance_name]

            new_name = self.tables['history'].table_object.get_new_name()
            self.instances[history_name].set_name(new_name)
            self.instances[history_name].instance.date_created = datetime.utcnow()
            self.instances[history_name].instance.last_modified = datetime.utcnow()

            self.background_save_instances[history_name] = self.instances[history_name].instance

            self.background_save_instances['history'] = self.tables['history'].table_object

        commit_status, commit_msg = self.oac.save_data_instance(instances,
                                                                list(self.background_save_instances.values()))

        if commit_status:
            if self.base_instance.instance.id not in commit_msg.keys():
                commit_msg[self.base_instance.instance.id] = {'id': self.base_instance.instance.id,
                                                              'name': self.base_instance.instance_name,
                                                              'table': self.base_instance.table_name,
                                                              'old_name': self.base_instance.old_name}

        return commit_status, commit_msg

    def rollback(self):
        self.oac.rollback()

    def list_instances(self):
        instance_list = {}

        for table_name, instances in self.instances.items():
            instance_list[table_name] = []
            for instance_name, instance in instances.items():
                instance_list[table_name].append(instance['instance'].name)

        return instance_list
