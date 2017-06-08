from flask import abort, g
from iggybase.core.table_collection import TableCollection
from iggybase.core.instance_data import InstanceData
from iggybase import g_helper
from collections import OrderedDict
from datetime import datetime
from iggybase.core.constants import ActionType, DatabaseEvent
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

        self.base_instance = None
        self.instance_counter = 1
        self.table_instances = OrderedDict()
        self.save_table_instances = OrderedDict()
        self.instance_names = {}
        self.action_results = {}

        self.tables = TableCollection(instance_data.keys(), depth)

        for table_name in self.tables.table_names:
            self.save_table_instances[table_name] = []
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

    def __iter__(self, table_name):
        return iter(self.table_instances[table_name])

    def __getitem__(self, table_name, instance_name):
        return self.table_instances[table_name][instance_name]

    def keys(self, table_name):
        return self.table_instances[table_name].keys()

    def items(self, table_name):
        return self.table_instances[table_name].items()

    def values(self, table_name):
        return self.table_instances[table_name].values()

    def reset(self):
        self.base_instance = None
        self.instance_counter = 1
        self.table_instances = OrderedDict()
        self.save_table_instances = OrderedDict()
        self.instance_names = {}
        self.action_results = {}

        for table_name in self.tables.table_names:
            self.save_table_instances[table_name] = []
            self.table_instances[table_name] = {}
            self.instance_names[table_name] = {}

    def set_instances(self, instances, parent_id=None, parent_link=None):
        instances_names = []
        
        for row in instances:
            instance = InstanceData(instance=row,
                                    form_index=self.instance_counter,
                                    parent_id=parent_id,
                                    parent_link=parent_link,
                                    table_data=self.tables[row.__tablename__].table_object)

            if instance.table_name not in self.table_instances.keys():
                self.table_instances[instance.table_name] = {}

            if instance.table_name not in self.tables.keys():
                self.tables.add_table(instance.table_name)

            if self.base_instance is None:
                self.base_instance = instance

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
                        self.set_instances([row['instance']], table_data.parent_link_field_display_name,
                                           row['parent_id'])
                        ids.append(row['instance'].id)
                elif table_data.level == 1:
                    instance_names = self.get_data(table_name, {'name': ['empty_row']})
                    self.table_instances[table_name][instance_names[0]].\
                        set_parent_id(table_data.parent_link_field_display_name, root_id)
                else:
                    self.get_data(table_name, {'name': ['empty_row']})
            elif table_data.link_type == "many":
                pass
            elif table_data.link_type == "table_id":
                pass

    def set_values(self, table_name, instance_name, field_values):
        for field_name, field_value in field_values.items():
            save = self.table_instances[table_name][instance_name].set_value(field_name, field_value)

        if save and instance_name not in self.save_table_instances[table_name]:
            self.save_table_instances[table_name].append(instance_name)

    def commit(self):
        instances = []
        background_save_instances = []
        instance_names = {}

        for table_name in self.table_instances.keys():
            for instance_name in self.save_table_instances[table_name]:
                instance_data = self.table_instances[table_name][instance_name]

                if instance_data.instance.date_created is None and not instance_data.new_instance:
                    self.table_instances[table_name][instance_name].instance.date_created = datetime.utcnow()

                self.table_instances[table_name][instance_name].instance.last_modified = datetime.utcnow()

                if instance_data.new_instance and not instance_data.name_set:
                    self.table_instances[table_name][instance_name].get_new_name()

                self.instance_names[instance_data.table_name][instance_data.old_name] = instance_data.instance_name
                instance_names[instance_data.instance_name] = instance_data.old_name

                self.table_instances[table_name][instance_name].set_save_data()
                instances.append(self.table_instances[table_name][instance_name].instance)
                background_save_instances += self.table_instances[table_name][instance_name].background_instances

        commit_status, commit_msg = self.oac.save_data_instance(instances, background_save_instances)

        if commit_status:
            actions = {'insert': {}, 'update': {}}
            for table_name in self.table_instances.keys():
                for instance_name in self.save_table_instances[table_name]:
                    instance_data = self.table_instances[table_name][instance_name]
                    table_name = instance_data.table_name

                    if instance_data.new_instance:
                        if table_name not in actions['insert'].keys():
                            actions['insert'][table_name] = Action(ActionType.TABLE,
                                                                   action_table=self.tables[table_name].table_id,
                                                                   action_event=DatabaseEvent.INSERT)

                        if actions['insert'][table_name]:
                            instance_data.execute_actions(actions['insert'][table_name])
                            self.action_results.update(instance_data.action_results)
                    else:
                        if table_name not in actions['update'].keys():
                            actions['update'][table_name] = Action(ActionType.TABLE,
                                                                   action_table=self.tables[table_name].table_id,
                                                                   action_event=DatabaseEvent.UPDATE)

                        if actions['update'][table_name]:
                            instance_data.execute_actions(actions['update'][table_name])
                            self.action_results.update(instance_data.action_results)

            if self.base_instance.instance.id not in commit_msg.keys():
                commit_msg[self.base_instance.instance.id] = {'id': self.base_instance.instance.id,
                                                              'name': self.base_instance.instance_name,
                                                              'table': self.base_instance.table_name,
                                                              'old_name': self.base_instance.old_name}

        return commit_status, commit_msg

    def rollback(self):
        self.oac.rollback()

    def list_instances(self, table_name):
        instance_list = {}

        for table_name, instances in self.table_instances[table_name].items():
            instance_list[table_name] = []
            for instance_name, instance in instances.items():
                instance_list[table_name].append(instance['instance'].name)

        return instance_list
