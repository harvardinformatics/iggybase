from flask import abort, g
from iggybase import utilities as util
from iggybase.core.field_collection import FieldCollection
from iggybase import g_helper
from collections import OrderedDict
import random
import datetime, time
import logging


class DataInstance:
<<<<<<< Updated upstream
    def __init__(self, table_name, instance_name = None):
        self.organization_access_control = g_helper.get_org_access_control()
        self.role_access_control = g_helper.get_role_access_control()

        self.table_name = table_name
        self.tables = OrderedDict()
        self.tables[table_name] = {'level': 0,
                                   'parent': None,
                                   'link_data': None,
                                   'table_object': util.get_table(table_name),
                                   'table_meta_data': self.role_access_control.has_access('TableObject',
                                                                                          {'name': table_name})}
=======
    def __init__(self, table_name, organization_access_control = None, field_collection = None):
        if organization_access_control is None:
            self.organization_access_control = g_helper.get_org_access_control()
        else:
            self.organization_access_control = organization_access_control

        role_access_control = g_helper.get_role_access_control()
>>>>>>> Stashed changes

        self.instance_counter = 1

        if self.tables[table_name]['table_meta_data'] is None:
            abort(403)

<<<<<<< Updated upstream
        self.instances = {}
        self.fields = {}
        self.history = []
        self.instance_name = None

        self.initialize_fields(table_name)

        if instance_name is not None:
            self.get_data(instance_name)
            self.instance_name = instance_name

        self.tables['history'] = {'level': 0,
                                   'parent': None,
                                   'link_data': None,
                                   'table_object': util.get_table('history'),
                                   'table_meta_data': self.role_access_control.has_access('TableObject',
                                                                                          {'name': 'history'})}
        self.instances['history'] = OrderedDict()
        self.fields['history'] = FieldCollection(None, 'history')
        self.fields['history'].set_fk_fields()

    def initialize_fields(self, table_name):
        if table_name not in self.instances.keys():
            self.instances[table_name] = OrderedDict()
            self.fields[table_name] = FieldCollection(None, table_name)
            self.fields[table_name].set_fk_fields()

    def get_data(self, instance_name = 'new', instance_id = None, table_name = None, instance = None):
        if table_name is None:
            table_name = self.table_name

        if instance is None:
            instance = self.get_instance(table_name, instance_name, instance_id)
            setattr(instance, 'instance_parent_id', None)

        if instance.name is None or instance.name == '' or instance_name == 'new':
            instance.name = 'new'

        if self.instance_name is None:
            self.instance_name = instance.name

        self.initialize_values(table_name, instance)

        self.instances[table_name][instance.name] = instance

    def add_new_instance(self, table_name, instance_name, instance = None):
        if instance is None:
            instance = self.get_instance(table_name, instance_name, None)

        setattr(instance, 'instance_parent_id', None)

        if instance.name is None or instance_name == 'new':
            instance.name = 'new_' + str(len(self.instances[table_name]))

        self.initialize_values(table_name, instance)

        self.instances[table_name][instance.name] = instance

        logging.info(table_name + ' new instance: ' + instance.name)
        return instance.name

    def get_instance(self, table_name, instance_name, instance_id):
        table_object = self.tables[table_name]['table_object']
=======
        self.table_name = table_name
        self.table_names = {table_name: table_name}
        self.table_objects = {table_name: util.get_table(table_name)}

        self.instance_name = None
        self.instances = {table_name: []}
        self.new = True
        self.history = None
        self.fields = {}
        self.field_values = {}
        self.original_values = {}
        self.descendants = {}

        self.initialize_fields(field_collection)

    def get_data(self, instance_name = 'new', instance_id = None):
        self.instances[self.table_name].append(self.get_instance(instance_name, instance_id))

        if self.instance[self.table_name][0].name is None or instance_name == 'new':
            self.instance_name = self.set_instance_name()
            self.new = True
        else:
            self.new = False
            self.instance_name = instance_name

        self.initialize_values()
>>>>>>> Stashed changes

        if instance_id is None:
<<<<<<< Updated upstream
            instance = self.organization_access_control.get_instance_data(table_object, {'name': instance_name})
        else:
            instance = self.organization_access_control.get_instance_data(table_object, {'id': instance_id})

        return instance

    def get_linked_instances(self, depth = 2):
        # start_time = time.time()
        #logging.info('get_linked_instances start time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        # logging.info('get_linked_instances self.tables[self.table_name][table_meta_data].name: ' +
        #              self.tables[self.table_name]['table_meta_data'].name)
        # logging.info('get_linked_instances self.tables[self.table_name][table_meta_data].id: ' +
        #              str(self.tables[self.table_name]['table_meta_data'].id))
        # logging.info('get_linked_instances depth: ' + str(depth))

        data = self.role_access_control.get_link_tables(self.tables[self.table_name]['table_meta_data'].name,
                                                        self.tables[self.table_name]['table_meta_data'].id, depth)

        # logging.info('data: ' + self.table_name)
        # logging.info(data)

        for index, link_data in enumerate(data):
            # link_data - {'parent': table_object_name, 'level': level, 'table_meta_data': table_meta_data,
            #              'link_data': row.TableObjectChildren, 'link_type': 'child'}
            table_name = link_data['table_meta_data'].name
            self.tables[table_name] = {'level': link_data['level'],
                                       'parent': link_data['parent'],
                                       'link_data': link_data['link_data'],
                                       'table_object': util.get_table(table_name),
                                       'table_meta_data': link_data['table_meta_data']}

            # logging.info('get_linked_instances self.tables[table_name]: ' + self.table_name)
            # logging.info(self.tables[table_name])

            self.initialize_fields(table_name)
=======
            instance = self.organization_access_control.get_instance_data(self.table_object,
                                                                               {'name': [instance_name]})
        else:
            instance = self.organization_access_control.get_instance_data(self.table_object,
                                                                               {'id': [instance_id]})
        return instance

    def get_link_instances(self, levels = 2):
        link_data, link_tables = self.role_access_control.get_link_tables(self.table_data.id, levels)

        if ids is None:
            ids = [self.instance.id]

        for descendant_table_name in descendant_table_names:
            self.descendants[descendant_table_name] = self.organization_access_control.get_descendant_data(ids,
                                                                                                           table_name)

    def initialize_values(self):
        self.history = []

        for field, meta_data in self.fields.items():
            if self.new and meta_data.default is not None:
                self.field_values[meta_data.Field.display_name] = meta_data.default
                self.original_values[meta_data.Field.display_name] = meta_data.default
            elif self.new:
                self.field_values[meta_data.Field.display_name] = None
                self.original_values[meta_data.Field.display_name] = None
            else:
                self.field_values[meta_data.Field.display_name] = getattr(self.instance[0], meta_data.Field.display_name)
                self.original_values[meta_data.Field.display_name] = getattr(self.instance[0], meta_data.Field.display_name)

    def initialize_fields(self, field_collection = None):
        if field_collection is None:
            field_collection = FieldCollection(None, self.table_name)
            field_collection.set_defaults()

        for field, meta_data in field_collection.fields.items():
            self.fields[meta_data.Field.display_name] = meta_data
            self.field_values[meta_data.Field.display_name] = None
            self.original_values[meta_data.Field.display_name] = None

    def update_field_values(self):
        for name, value in self.field_values.items():
            self.field_values[name] = getattr(self.instance[0], name)
            self.original_values[name] = getattr(self.instance[0], name)
>>>>>>> Stashed changes

            if link_data['level'] == 1:
                ids = [self.instances[self.table_name][self.instance_name].id]

            if link_data['link_type'] == "child":
                # logging.info('child_rows start time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

                # logging.info('get_linked_instances table_name: ' + table_name)
                # logging.info('get_linked_instances link_data[link_data].child_link_field_id: ' +
                #              str(link_data['link_data'].child_link_field_id))
                # logging.info('get_linked_instances ' + table_name + ' ids')
                # logging.info(ids)

                child_rows = self.organization_access_control. \
                    get_descendant_data(table_name, link_data['link_data'].child_link_field_id, ids)

                # logging.info('child_rows end time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

                # logging.info('child_rows: ' + table_name)
                # logging.info(child_rows)

                ids = []

                if child_rows:
                    for row in child_rows:
                        # logging.info('instance time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
                        self.get_data(None, row.id, table_name, row)
                        self.instance_counter += 1
                        ids.append(row.id)
                else:
                    self.get_data('new', None, table_name)

            elif link_data['link_type'] == "many":
                pass

        # logging.info('get_linked_instances time: ' + str(time.time() - start_time))
        #logging.info('get_linked_instances end time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

    def initialize_values(self, table_name, instance):
        # logging.info('table_name: ' + table_name)
        # logging.info(self.tables)

        if self.tables[table_name]['parent'] is None:
            self.fields[table_name].set_defaults()
        else:
            self.fields[table_name].set_defaults({self.tables[table_name]['parent']: instance.instance_parent_id})

        if instance.name == 'new':
            for field, meta_data in self.fields[table_name].fields.items():
                if meta_data.default is not None:
                    setattr(instance, meta_data.Field.display_name, meta_data.default)
                else:
                    setattr(instance, meta_data.Field.display_name, None)

    def set_value(self, field_name, field_value, table_name = None, instance_name = None):
        if table_name is None:
            table_name = self.table_name
        if instance_name is None:
            instance_name = self.instance_name

        if self.fields[table_name].fields[table_name + "|" + field_name].is_foreign_key:
            field_value = self.set_foreign_key_field_id(table_name, field_name, field_value)

        if table_name != 'history':
            new_key = self.add_new_instance('history', 'new')

            self.set_value({'table_object_id': self.tables[table_name]['table_meta_data'].id,
                            'field_id': self.fields[table_name].fields[table_name + "|" + field_name].Field.id,
                            'organization_id': self.set_organization_id(self.instances['history'][new_key]),
                            'instance_name': instance_name,
                            'old_value': getattr(self.instances[table_name][instance_name], field_name, None),
                            'user_id': g.user.id,
                            'new_value': field_value},
                           'history',
                           new_key)

        setattr(self.instances[table_name][instance_name], field_name, field_value)

    def set_values(self, field_values = {}, table_name = None, instance_name = None):
        if table_name is None:
            table_name = self.table_name
        if instance_name is None:
            instance_name = self.instance_name

        if 'organization_id' in field_values:
            self.set_value('organization_id', field_values['organization_id'], table_name, instance_name)
            field_values.pop('organization_id')

        for field_name, field_value in field_values.items():
            self.set_value(field_name, field_value, table_name, instance_name)

    def set_foreign_key_field_id(self, table_name, field, value):
        if table_name is None:
            table_name = self.table_name

        # logging.info(table_name)
        # logging.info(self.fields[table_name].fields)

        fk_field_display = self.fields[table_name].fields[table_name + "|" + field].FK_Field

        fk_table_data = self.fields[table_name].fields[table_name + "|" + field].FK_TableObject

        fk_table_object = util.get_table(fk_table_data.name)

        # logging.info(fk_table_object)
        # logging.info(fk_field_display)

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

        return self.field_values[table_name][instance_name][field_name]

    def get_values(self, table_name = None, instance_name = None):
        if table_name is None:
            table_name = self.table_name
        if instance_name is None:
            instance_name = self.instance_name

        return self.field_values[table_name][instance_name]

    def save(self):
        # logging.info('name at save: ' )
        # logging.info(self.instance_name)
        saved_data = {}

        instance_names = {}

        table_data = (x for x in self.instances.keys() if x != 'history')

        for table_name in table_data:
            instances = self.instances[table_name]

            for instance_name, instance in instances.items():
                if 'new' in instance_name and (instance.name is None or instance.name == 'new'):
                    instance.name = self.set_instance_name(table_name)

                instance_names[instance_name] = instance.name

<<<<<<< Updated upstream
                if instance.date_created is None:
                    instance.date_created = datetime.datetime.utcnow()

                instance.last_modified = datetime.datetime.utcnow()

                save_msg = self.organization_access_control.save_data_instance(instance)
                saved_data[save_msg['id']] = save_msg
=======
        for instance in self.instances:
            for field_name, value in self.field_values.items():
                if field_name == 'name' and (value is None or value == ''):
                    setattr(self.instance[0], field_name, self.instance_name)
                else:
                    setattr(self.instance[0], field_name, value)

            if self.table_name != 'history':
                self.changed_values()
                for history in self.history:
                    history_instance = DataInstance('history')
                    history_instance.get_data()
                    history_instance.set_values(history)
                    history_instance.save()

        save_msg = self.organization_access_control.save_data_instance(self.instance[0])
>>>>>>> Stashed changes

        for instance in self.instances['history']:
            if instance.instance_name in instance_names.keys():
                instance.instance_name = instance_names[instance_name]

<<<<<<< Updated upstream
            instance.name = self.set_instance_name('history')
            instance.date_created = datetime.datetime.utcnow()
            instance.last_modified = datetime.datetime.utcnow()

            self.organization_access_control.save_data_instance(instance)

        self.organization_access_control.commit

        return saved_data

    def set_instance_name(self, table_name = None):
        if table_name is None:
            table_name = self.table_name
=======
        return save_msg
>>>>>>> Stashed changes

        if self.tables[table_name]['table_meta_data'].new_name_prefix is not None and \
                        self.tables[table_name]['table_meta_data'].new_name_prefix != "":
            instance_name = self.organization_access_control.get_new_name(table_name)
        else:
            instance_name = table_name + str(random.randint(1000000000, 9999999999))

        # logging.info('name at set_instance_name: ' + instance_name)

        return instance_name

    def set_organization_id(self, instance):
        if instance.organization_id is not None:
            row_org_id = instance.organization_id

            if not isinstance(row_org_id, int):
                org_table_object = util.get_table('organization')

                org_record = self.organization_access_control.session.query(org_table_object). \
                    filter_by(name = row_org_id).first()

                if org_record:
                    return org_record.id

        if self.organization_access_control.current_org_id is not None:
            return self.organization_access_control.current_org_id
        else:
            return 1