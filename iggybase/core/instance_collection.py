from flask import abort, g
from iggybase.core.table_collection import TableCollection
from iggybase.core.instance_data import InstanceData
from iggybase import utilities as util
from iggybase import g_helper
from collections import OrderedDict
import datetime
import logging


class InstanceCollection:
    def __init__(self, depth = 2, instance_data={}):
        self.rac = g_helper.get_role_access_control()
        self.oac = g_helper.get_org_access_control()

        self.tables = TableCollection(instance_data.keys(), depth)

        self.instances = OrderedDict()
        self.table_instances = OrderedDict()
        for table_name in self.tables.table_names:
            self.table_instances[table_name] = {}

        self.instance_names = []
        self.background_save_instances = {}

        for table_name, instance_names in instance_data.items():
            if instance_names:
                if isinstance(instance_names, str):
                    self.get_data(table_name, {'name': [instance_names]})
                else:
                    self.get_data(table_name, {'name': instance_names})

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
            instance = InstanceData(row, row.name, len(self.instance_names))

            self.initialize_values(instance)

            self.instances[instance.instance_name] = instance
            self.table_instances[instance.table_name][instance.instance_name] = instance

            instances_names.append(instance.instance_name)
            
            self.instance_names.append(instance.instance_name)
            
        return instances_names

    def get_data(self, table_name, instance_dict):
        instances_names = []

        for key, values in instance_dict.items():
            instances = self.oac.get_instance_data(self.tables[table_name].table_instance, {key: values})

            tmp_instances_names = self.set_instances(instances)

            instances_names += tmp_instances_names
            self.instance_names += tmp_instances_names

        return instances_names

    def add_new_instances(self, table_name, quantity=0):
        instance_names = []

        i = 0
        while i < quantity:
            instance_names.append(self.add_new_instance(table_name))
            i += 1

        return instance_names

    def add_new_instance(self, table_name, instance_name='new', parent_link_field=None, parent_id=None):
        instance_name = self.get_data(table_name, {'name': [instance_name]})

        if parent_link_field is not None:
            setattr(self.instances[instance_name], parent_link_field, parent_id)

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
                        self.instances[instance_names[0]].parent_id = row['parent_id']
                        ids.append(row['instance'].id)
                else:
                    instance_names = self.get_data(table_name, {'name': 'empty_row'})
                    if table_data.level == 1:
                        self.instances[instance_names[0]].parent_id = root_id
            elif table_data.link_type == "many":
                pass
            elif table_data.link_type == "table_id":
                pass

    def initialize_values(self, instance):
        table_name = instance.table_name
        if self.tables[table_name].parent is None:
            self.tables[table_name].fields.set_defaults()
        else:
            self.tables[table_name].fields.set_defaults({self.tables[table_name].parent: instance.parent_id,
                                                         'link_display_name': self.tables[table_name].\
                                                        parent_link_field_display_name})

        if instance.new_instance:
            for field, meta_data in self.tables[table_name].fields.items():
                if meta_data.default is not None and meta_data.default != '':
                    if meta_data.Field.data_type_id == 3:
                        if meta_data.default.lower == 'true' or meta_data.default == '1':
                            setattr(instance.instance, meta_data.Field.display_name, True)
                        else:
                            setattr(instance.instance, meta_data.Field.display_name, False)
                    elif meta_data.default == 'current_user':
                        setattr(instance.instance, meta_data.Field.display_name, g.user.id)
                    elif meta_data.default == 'current_date':
                        setattr(instance.instance, meta_data.Field.display_name,
                                datetime.date.today().strftime('%Y-%d-%m'))
                    else:
                        setattr(instance.instance, meta_data.Field.display_name, meta_data.default)
                elif meta_data.Field.display_name == 'organization_id':
                    org_id = self.set_organization_id()
                    setattr(instance.instance, 'organization_id', org_id)
                elif meta_data.Field.data_type_id == 3:
                    setattr(instance.instance, meta_data.Field.display_name, False)

    def set_foreign_key_field_id(self, table_name, field, value):
        if isinstance( value, int ):
            return value

        fk_field_display = self.tables[table_name].fields[table_name + "|" + field].FK_Field

        fk_table_data = self.tables[table_name].fields[table_name + "|" + field].FK_TableObject

        fk_table_object = util.get_table(fk_table_data.name)
        if fk_table_data.name == 'field':
            res = self.oac.session.query(fk_table_object). \
                filter(getattr(fk_table_object, fk_field_display.display_name) == value). \
                filter(fk_table_object.table_object_id == self.tables[table_name].table_object.id)

            fk_id = res.first()
        else:
            fk_id = self.oac.session.query(fk_table_object). \
                filter(getattr(fk_table_object, fk_field_display.display_name) == value).first()

        if fk_id:
            return fk_id.id
        else:
            return None

    def set_values(self, instance_name, field_values = {}):
        for field_name, field_value in field_values.items():
            self.set_value(instance_name, field_name, field_value)

    def set_value(self, instance_name, field_name, field_value):
        exclude_list = ['id', 'last_modified', 'date_created']

        table_name = self.instances[instance_name].table_name
        field = self.tables[table_name].fields[table_name + "|" + field_name]
        instance = self.instances[instance_name].instance
        instance_value = getattr(instance, field_name)

        if field.is_foreign_key and table_name != 'long_text':
            field_value = self.set_foreign_key_field_id(table_name, field_name, field_value)
        elif field.DataType.name.lower() == 'boolean' and field_value == True or field_value == 'True':
            field_value = 1

        # logging.info('field_name: ' + field_name + "   field_value: " + str(field_value) + " type: " +
        #              str(type(field_value)) + "   getattr: " +
        #              str(instance_value) + " type: " +
        #              str(type(instance_value)))

        if (table_name != 'history' and field_name not in exclude_list and
                ((instance_value is None and field_value is not None) or
                 (instance_value is not None and field_value is None) or field_value != instance_value) and
                ((not (field_name == 'name' and field_value is None and instance.new_instance) and
                  self.tables[table_name].level == 0) or (field_name != 'name'))):
            instance.save = True
            new_key = self.add_new_instance('history')

            self.set_values(new_key,
                            {'table_object_id': self.tables[table_name].table_object.id,
                             'field_id': field.Field.id,
                             'organization_id':  getattr(instance, 'organization_id'),
                             'instance_name': instance_name,
                             'old_value': getattr(instance, field_name, None),
                             'user_id': g.user.id,
                             'new_value': field_value})

        if field_name not in exclude_list:
            setattr(instance, field_name, field_value)

    def commit(self):
        inst_names = {}
        save_instances = []

        for instance_name, instance_data in self.instances.items():
            if instance_data.table_name == 'history' or not instance_data.save:
                continue

            if instance_data.new_instance:
                instance_data.set_new_name(self.tables[instance_data.table_name].table_object)
                self.background_save_instances[instance_data.table_name] = \
                    self.tables[instance_data.table_name].table_object

            inst_names[instance_data.old_name] = instance_data.instance_name

            if instance_data.instance.date_created is None:
                instance_data.instance.date_created = datetime.datetime.utcnow()

            instance_data.instance.last_modified = datetime.datetime.utcnow()
            save_instances.append(instance_data.instance)

        for history_name, instance_data in self.table_instances['history'].items():
            if instance_data.instance.instance_name in inst_names.keys():
                instance_data.instance.instance_name = inst_names[instance_data.instance.instance_name]

            instance_data.set_new_name(self.tables['history'].table_object)
            instance_data.instance.date_created = datetime.datetime.utcnow()
            instance_data.instance.last_modified = datetime.datetime.utcnow()

            self.background_save_instances[history_name] = instance_data.instance

        self.background_save_instances['history'] = self.tables['history'].table_object

        commit_status, commit_msg = self.oac.save_data_instance(save_instances,
                                                                list(self.background_save_instances.values()))

        if commit_status:
            base_instance = next(iter(self.items()))[1]
            logging.info('base_instance: ' + str(base_instance.instance.id))
            if base_instance.instance.id not in commit_msg.keys() and base_instance.new_instance == False:
                commit_msg[base_instance.instance.id] = {'id': base_instance.instance.id,
                                                         'name': base_instance.instance_name,
                                                         'table': base_instance.table_name,
                                                         'old_name': base_instance.old_name}

        return commit_status, commit_msg

    def commit_instance(self, instance_name):
        instance_data = self.instances[instance_name]

        if instance_data.new_instance:
            instance_data.set_new_name(self.tables[instance_data.table_name].table_object)
            self.background_save_instances[instance_data.table_name] = \
                self.tables[instance_data.table_name].table_object

        if instance_data.instance.date_created is None:
            instance_data.instance.date_created = datetime.datetime.utcnow()

        instance_data.instance.last_modified = datetime.datetime.utcnow()
        save_instances = [instance_data.instance]

        for history_name, history_data in self.table_instances['history'].items():
            if history_data.instance.instance_name == instance_data.old_name:
                history_data.instance.instance_name = instance_data.instance_name

            history_data.set_new_name(self.tables['history'].table_object)
            history_data.instance.date_created = datetime.datetime.utcnow()
            history_data.instance.last_modified = datetime.datetime.utcnow()

            self.background_save_instances[history_name] = history_data.instance

        commit_status, commit_msg = self.oac.save_data_instance(save_instances)

        if commit_status:
            instance_data.save = False

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

    def set_organization_id(self, row_org_id = None):
        if row_org_id is not None:
            if isinstance(row_org_id, int):
                return row_org_id
            else:
                org_table_object = util.get_table('organization')

                org_record = self.oac.session.query(org_table_object). \
                    filter_by(name = row_org_id).first()

                if org_record:
                    return org_record.id

        if self.oac.current_org_id is not None:
            return self.oac.current_org_id
        else:
            return 1