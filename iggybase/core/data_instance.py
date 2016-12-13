from flask import abort, g
from iggybase import utilities as util
from iggybase.core.field_collection import FieldCollection
from iggybase import g_helper
from collections import OrderedDict
import datetime
import logging

class DataInstance:
    def __init__(self, table_name, instance_name = None, depth = 2):
        self.role_access_control = g_helper.get_role_access_control()
        self.organization_access_control = g_helper.get_org_access_control()

        self.table_name = table_name
        self.tables = OrderedDict()
        self.fields = {}
        self.instances = {}
        self.instance_names = {}
        if instance_name is not None or instance_name != 'new':
            self.get_tables(depth)

        self.instance_counter = 0

        if self.tables[table_name]['table_meta_data'] is None:
            abort(403)

        self.instance_id = None
        self.instance_name = None
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

        if self.tables[table_name]['level'] == 1 and 'new' in instance.name and \
                        self.tables[table_name]['link_display_name'] is not None:
            setattr(instance, self.tables[table_name]['link_display_name'], self.instance_id)

        instance = {'instance': instance, 'parent_id': None, 'save': False}

        self.initialize_values(table_name, instance)

        self.instances[table_name][instance['instance'].name] = instance

        return instance['instance'].name

    def set_name(self, table_name, instance, instance_name = 'new'):
        self.instance_counter += 1

        if instance.name is None or instance.name == '' or instance_name == 'new':
            instance.name = 'new_' + str(len(self.instances[table_name]))

        if self.instance_name is None:
            self.instance_name = instance.name
            self.instance_id = instance.id

    def get_instance(self, table_name, instance_name, instance_id):
        if instance_id is None:
            instance = self.organization_access_control.get_instance_data(self.tables[table_name]['table_object'],
                                                                          {'name': instance_name})
        else:
            instance = self.organization_access_control.get_instance_data(self.tables[table_name]['table_object'],
                                                                          {'id': instance_id})

        return instance

    def get_tables(self, depth = 2):
        self.tables[self.table_name] = {'level': 0,
                                        'link_display_name': None,
                                        'parent': None,
                                        'link_data': None,
                                        'link_type': None,
                                        'table_object': util.get_table(self.table_name),
                                        'table_meta_data': (self.role_access_control.has_access
                                                            ('TableObject', {'name': self.table_name}))}
        self.initialize_fields(self.table_name)

        self.tables['history'] = {'level': 0,
                                  'parent': None,
                                  'link_display_name': None,
                                  'link_data': None,
                                  'link_type': None,
                                  'table_object': util.get_table('history'),
                                  'table_meta_data': self.role_access_control.has_access('TableObject',
                                                                                          {'name': 'history'})}
        self.initialize_fields('history')

        if depth > 0 and self.tables[self.table_name]['table_meta_data']:
            data = self.role_access_control.get_link_tables(self.tables[self.table_name]['table_meta_data'].name,
                                                            self.tables[self.table_name]['table_meta_data'].id, depth)

            for index, link_data in enumerate(data):
                # link_data - {'parent': table_object_name, 'level': level, 'table_meta_data': table_meta_data,
                #              'link_data': row.TableObjectChildren, 'link_type': 'child'}
                table_name = link_data['table_meta_data'].name
                self.initialize_fields(table_name)
                link_display_name = self.fields[table_name].fields_by_id[(link_data['link_data'].child_table_object_id,
                                                                          link_data['link_data'].child_link_field_id)] \
                    .Field.display_name

                self.tables[table_name] = {'level': link_data['level'],
                                           'parent': link_data['parent'],
                                           'link_data': link_data['link_data'],
                                           'table_object': util.get_table(table_name),
                                           'table_meta_data': link_data['table_meta_data'],
                                           'link_display_name': link_display_name,
                                           'link_type': link_data['link_type']}

    def initialize_fields(self, table_name):
        self.instances[table_name] = OrderedDict()
        if table_name == 'history':
            self.fields[table_name] = FieldCollection(None, table_name, {}, False)
        else:
            self.fields[table_name] = FieldCollection(None, table_name)
        self.fields[table_name].set_fk_fields()

    def get_linked_instances(self):
        for table_name, table_data in self.tables.items():
            if table_data['level'] == 0:
                continue
            elif table_data['level'] == 1:
                ids = [self.instance_id]

            if table_data['link_type'] == "child":
                child_rows = self.organization_access_control. \
                    get_descendant_data(table_name, table_data['link_data'].child_link_field_id, ids)

                ids = []

                # always increment instance, since empty table rows will be added to the form
                if child_rows:
                    for row in child_rows:
                        self.get_data(None, row['instance'].id, table_name, row['instance'], row['parent_id'])
                        ids.append(row['instance'].id)
                elif table_data['level'] == 1:
                    self.get_data('new', None, table_name, None,
                                  self.instances[self.table_name][self.instance_name]['instance'].id)
                else:
                    self.get_data('new', None, table_name)

            elif table_data['link_type'] == "many":
                pass

    def initialize_values(self, table_name, instance):
        if self.tables[table_name]['parent'] is None:
            self.fields[table_name].set_defaults()
        else:
            self.fields[table_name].set_defaults({self.tables[table_name]['parent']: instance['parent_id']})

        if 'new' in instance['instance'].name:
            for field, meta_data in self.fields[table_name].fields.items():
                if meta_data.default is not None and meta_data.default != '':
                    setattr(instance['instance'], meta_data.Field.display_name, meta_data.default)
                elif meta_data.Field.display_name == 'organization_id':
                    org_id = self.set_organization_id()
                    setattr(instance['instance'], 'organization_id', org_id)
                elif meta_data.Field.data_type_id == 3:
                    setattr(instance['instance'], meta_data.Field.display_name, False)

    def set_foreign_key_field_id(self, table_name, field, value):
        if isinstance( value, int ):
            return value

        fk_field_display = self.fields[table_name].fields[table_name + "|" + field].FK_Field

        fk_table_data = self.fields[table_name].fields[table_name + "|" + field].FK_TableObject

        fk_table_object = util.get_table(fk_table_data.name)
        if fk_table_data.name == 'field':
            res = self.organization_access_control.session.query(fk_table_object). \
                filter(getattr(fk_table_object, fk_field_display.display_name) == value). \
                filter(fk_table_object.table_object_id == self.tables[table_name]['table_meta_data'].id)

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

        if self.fields[table_name].fields[table_name + "|" + field_name].is_foreign_key:
            field_value = self.set_foreign_key_field_id(table_name, field_name, field_value)

        if table_name != 'history' and field_name not in exclude_list and \
                ((getattr(self.instances[table_name][instance_name]['instance'], field_name) is None and
                  field_value is not None) or
                 field_value != getattr(self.instances[table_name][instance_name]['instance'], field_name)) and \
                not (field_name == 'name' and field_value is None and
                     'new' in self.instances[table_name][instance_name]['instance'].name):
            self.instances[table_name][instance_name]['save'] = True
            new_key = self.add_new_instance('history', 'new')

            self.set_values({'table_object_id': self.tables[table_name]['table_meta_data'].id,
                             'field_id': self.fields[table_name].fields[table_name + "|" + field_name].Field.id,
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
        self.instance_names = {}
        inst_names = {}
        save_instances = []
        background_save_instances = []

        for table_name, instances in self.instances.items():
            if table_name == 'history':
                continue

            saved_new = False
            for instance_name, instance in instances.items():
                if not instance['save']:
                    continue

                if 'new' in instance_name and (instance['instance'].name is None or 'new' in instance['instance'].name):
                    instance['instance'].name = self.set_instance_name(table_name)
                    saved_new = True

                # logging.error("instance['instance'].name: " + instance['instance'].name)
                # logging.error("instance_name: " + instance_name)
                self.instance_names[(instance_name, table_name)] = instance['instance'].name
                inst_names[instance_name] = instance['instance'].name

                if instance['instance'].date_created is None:
                    instance['instance'].date_created = datetime.datetime.utcnow()

                instance['instance'].last_modified = datetime.datetime.utcnow()

                save_instances.append(instance['instance'])

            if saved_new:
                background_save_instances.append(self.tables[table_name]['table_meta_data'])

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
            if self.instance_id not in commit_msg:
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

        instance_name = self.tables[table_name]['table_meta_data'].get_new_name()

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
