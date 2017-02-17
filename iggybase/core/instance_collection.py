from flask import abort, g
from iggybase.core.table_collection import TableCollection
from iggybase import utilities as util
from iggybase import g_helper
from collections import OrderedDict
import datetime
import logging


class InstanceCollection:
    def __init__(self, table_name, instance_name = None, depth = 2):
        self.role_access_control = g_helper.get_role_access_control()
        self.organization_access_control = g_helper.get_org_access_control()

        self.table_name = table_name

        self.tables = TableCollection(table_name, depth)

        self.instances = {}
        for table_name, display_name in self.tables.table_names.items():
            self.instances[table_name] = OrderedDict()

        self.instance_names = {}

        self.instance_counter = 0

        self.instance_id = None
        self.instance_name = None
        self.new = False

        if instance_name is not None:
            self.get_data(instance_name)

    def get_data(self, instance_name = 'new', instance_id = None, table_name = None, instance = None,
                 instance_parent_id = None):
        if table_name is None:
            table_name = self.table_name

        if instance is None:
            instance = self.get_instance(table_name, instance_name, instance_id)

        self.set_name(table_name, instance, instance_name)

        instance = {'instance': instance, 'parent_id': instance_parent_id, 'save': False}

        self.initialize_values(table_name, instance)

        self.instances[table_name][instance['instance'].name] = instance

    def get_multiple_data(self, instance_names = []):
        for i, instance_name in enumerate(instance_names):
            self.instance_name = instance_name

            instance = self.get_instance(self.table_name, instance_name, None)

            self.set_name(self.table_name, instance, instance_name)

            instance = {'instance': instance, 'parent_id': None, 'save': False}

            self.initialize_values(self.table_name, instance)

            self.instances[self.table_name][instance['instance'].name] = instance

    def add_new_instances(self, table_name, quantity = 0):
        instance_names = []

        i = 0
        while i < quantity:
            instance_names.append(self.add_new_instance(table_name, 'new'))
            i += 1

        return instance_names

    def add_new_instance(self, table_name, instance_name, instance = None):
        if instance is None:
            instance = self.get_instance(table_name, instance_name, None)

        self.set_name(table_name, instance, instance_name)

        if self.tables.level[table_name] == 1 and 'new' in instance.name and \
                        self.tables.link_display_name[table_name] is not None:
            setattr(instance, self.tables.link_display_name[table_name], self.instance_id)

        instance = {'instance': instance, 'parent_id': None, 'save': False}

        self.initialize_values(table_name, instance)

        self.instances[table_name][instance['instance'].name] = instance

        return instance['instance'].name

    def set_name(self, table_name, instance, instance_name = 'new'):
        self.instance_counter += 1

        if instance_name == 'empty_row':
            instance.new_instance = True
            instance.name = instance_name
        elif instance.name is None or instance.name == '' or instance_name == 'new':
            instance.name = 'new_' + str(len(self.instances[table_name]))
            instance.new_instance = True
        else:
            instance.new_instance = False

        instance.old_name = instance.name

        if self.instance_name is None:
            self.instance_name = instance.name
            self.instance_id = instance.id
            self.new = instance.new_instance

    def get_instance(self, table_name, instance_name, instance_id):
        if instance_id is None:
            instance = self.organization_access_control.get_instance_data(self.tables.table_object[table_name],
                                                                          {'name': instance_name})
        else:
            instance = self.organization_access_control.get_instance_data(self.tables.table_object[table_name],
                                                                          {'id': instance_id})

        return instance

    def get_linked_instances(self):
        for table_name, table_data in self.tables.table_object.items():
            if self.tables.level[table_name] == 1:
                ids = [self.instance_id]

            if self.tables.link_type[table_name] == "child":
                child_rows = self.organization_access_control. \
                    get_descendant_data(table_name, self.tables.link_data[table_name].child_link_field_id, ids)

                ids = []

                # always increment instance, since empty table rows will be added to the form
                if child_rows:
                    for row in child_rows:
                        self.get_data(None, row['instance'].id, table_name, row['instance'], row['parent_id'])
                        ids.append(row['instance'].id)
                elif self.tables.level[table_name] == 1:
                    self.get_data('empty_row', None, table_name, None,
                                  self.instances[self.table_name][self.instance_name]['instance'].id)
                else:
                    self.get_data('empty_row', None, table_name)

            elif self.tables.link_type[table_name] == "many":
                pass
            elif self.tables.link_type[table_name] == "table_id":
                pass

    def initialize_values(self, table_name, instance):
        if self.tables.parent[table_name] is None:
            self.tables.fields[table_name].set_defaults()
        else:
            self.tables.fields[table_name].set_defaults({self.tables.parent[table_name]: instance['parent_id'],
                                                         'link_display_name': self.tables.link_display_name[table_name]})

        if instance['instance'].new_instance:
            for field, meta_data in self.tables.fields[table_name].fields.items():
                if meta_data.default is not None and meta_data.default != '':
                    if meta_data.Field.data_type_id == 3:
                        if meta_data.default.lower == 'true' or meta_data.default == '1':
                            setattr(instance['instance'], meta_data.Field.display_name, True)
                        else:
                            setattr(instance['instance'], meta_data.Field.display_name, False)
                    else:
                        setattr(instance['instance'], meta_data.Field.display_name, meta_data.default)
                elif meta_data.Field.display_name == 'organization_id':
                    org_id = self.set_organization_id()
                    setattr(instance['instance'], 'organization_id', org_id)
                elif meta_data.Field.data_type_id == 3:
                    setattr(instance['instance'], meta_data.Field.display_name, False)

    def set_foreign_key_field_id(self, table_name, field, value):
        if isinstance( value, int ):
            return value

        fk_field_display = self.tables.fields[table_name].fields[table_name + "|" + field].FK_Field

        fk_table_data = self.tables.fields[table_name].fields[table_name + "|" + field].FK_TableObject

        fk_table_object = util.get_table(fk_table_data.name)
        if fk_table_data.name == 'field':
            res = self.organization_access_control.session.query(fk_table_object). \
                filter(getattr(fk_table_object, fk_field_display.display_name) == value). \
                filter(fk_table_object.table_object_id == self.tables.table_meta_data[table_name].id)

            fk_id = res.first()
        else:
            fk_id = self.organization_access_control.session.query(fk_table_object). \
                filter(getattr(fk_table_object, fk_field_display.display_name) == value).first()

        if fk_id:
            return fk_id.id
        else:
            return None

    def get_value(self, field_name, table_name = None, instance_name = None):
        if table_name is None:
            table_name = self.table_name
        if instance_name is None:
            instance_name = self.instance_name

        return getattr(self.instances[table_name][instance_name]['instance'], field_name)

    def get_values(self, table_name = None, instance_name = None):
        if table_name is None:
            table_name = self.table_name
        if instance_name is None:
            instance_name = self.instance_name

        return self.instances[table_name][instance_name]['instance'].values()

    def set_values(self, field_values = {}, table_name = None, instance_name = None):
        if table_name is None:
            table_name = self.table_name
        if instance_name is None:
            instance_name = self.instance_name

        for field_name, field_value in field_values.items():
            self.set_value(field_name, field_value, table_name, instance_name)

    def set_value(self, field_name, field_value, table_name = None, instance_name = None):
        if table_name is None:
            table_name = self.table_name
        if instance_name is None:
            instance_name = self.instance_name

        exclude_list = ['id', 'last_modified', 'date_created']

        if self.tables.fields[table_name].fields[table_name + "|" + field_name].is_foreign_key:
            field_value = self.set_foreign_key_field_id(table_name, field_name, field_value)
        elif (self.tables.fields[table_name].fields[table_name + "|" + field_name].DataType.name).lower() == 'boolean' and \
                        field_value == True or field_value == 'True':
                field_value = 1;

        instance_value = getattr(self.instances[table_name][instance_name]['instance'], field_name)

        if (table_name != 'history' and field_name not in exclude_list and
                ((instance_value is None and field_value is not None) or
                 (instance_value is not None and field_value is None) or field_value != instance_value) and
                ((not (field_name == 'name' and field_value is None and
                  self.instances[table_name][instance_name]['instance'].new_instance) and
                  self.tables.level[table_name] == 0) or (field_name != 'name'))):
            self.instances[table_name][instance_name]['save'] = True
            new_key = self.add_new_instance('history', 'new')

            logging.info('field_name: ' + field_name + "   field_value: " + str(field_value) + " type: " +
                         str(type(field_value)) + "   getattr: " +
                         str(instance_value) + " type: " +
                         str(type(instance_value)))

            self.set_values({'table_object_id': self.tables.table_meta_data[table_name].id,
                             'field_id': self.tables.fields[table_name].fields[table_name + "|" + field_name].Field.id,
                             'organization_id':  getattr(self.instances[table_name][instance_name]['instance'],
                                                         'organization_id'),
                             'instance_name': instance_name,
                             'old_value': getattr(self.instances[table_name][instance_name]['instance'],
                                                  field_name, None),
                             'user_id': g.user.id,
                             'new_value': field_value},
                            'history',
                            new_key)

        if field_name not in exclude_list:
            setattr(self.instances[table_name][instance_name]['instance'], field_name, field_value)

    def commit(self):
        inst_names = {}
        save_instances = []
        background_save_instances = []
        for table_name, instances in self.instances.items():
            if table_name == 'history':
                continue

            saved_new_name = False
            for instance_name, instance in instances.items():
                if not instance['save']:
                    continue

                if instance['instance'].new_instance == True and (instance['instance'].name is None or
                                                                  'new' in instance['instance'].name or
                                                                  instance['instance'].name == 'empty_row'):
                    instance['instance'].name = self.set_instance_name(table_name)
                    saved_new_name = True

                self.instance_names[(instance_name, table_name)] = instance['instance'].name
                inst_names[instance_name] = instance['instance'].name

                if instance['instance'].date_created is None:
                    instance['instance'].date_created = datetime.datetime.utcnow()

                instance['instance'].last_modified = datetime.datetime.utcnow()

                save_instances.append(instance['instance'])

            if saved_new_name:
                background_save_instances.append(self.tables.table_meta_data[table_name])

        for history_name, instance in self.instances['history'].items():
            if instance['instance'].instance_name in inst_names.keys():
                instance['instance'].instance_name = inst_names[instance['instance'].instance_name]

            instance['instance'].name = self.set_instance_name('history')
            instance['instance'].date_created = datetime.datetime.utcnow()
            instance['instance'].last_modified = datetime.datetime.utcnow()

            background_save_instances.append(instance['instance'])

        commit_status, commit_msg = self.organization_access_control.save_data_instance(save_instances,
                                                                                        background_save_instances)

        if commit_status:
            if self.instance_id not in commit_msg and self.new == False:
                commit_msg[self.instance_id] = {'id': self.instance_id, 'name': self.instance_name,
                                                'table': self.table_name, 'old_name': self.instance_name}

        return commit_status, commit_msg

    def rollback(self):
        self.organization_access_control.rollback()

    def list_instances(self):
        instance_list = {}

        for table_name, instances in self.instances.items():
            instance_list[table_name] = []
            for instance_name, instance in instances.items():
                instance_list[table_name].append(instance['instance'].name)

        return instance_list

    def set_instance_name(self, table_name = None):
        if table_name is None:
            table_name = self.table_name

        instance_name = self.tables.table_meta_data[table_name].get_new_name()

        return instance_name

    def set_organization_id(self, row_org_id = None):
        if row_org_id is not None:
            if isinstance(row_org_id, int):
                return row_org_id
            else:
                org_table_object = util.get_table('organization')

                org_record = self.organization_access_control.session.query(org_table_object). \
                    filter_by(name = row_org_id).first()

                if org_record:
                    return org_record.id

        if self.organization_access_control.current_org_id is not None:
            return self.organization_access_control.current_org_id
        else:
            return 1
