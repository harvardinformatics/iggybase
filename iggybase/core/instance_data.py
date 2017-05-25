from iggybase import g_helper
from iggybase import models
from iggybase.admin.models import TableObject
from flask import g, session
import datetime
import logging

class InstanceData():
    def __init__(self, *args, **kwargs):
        if not(('table_name' in kwargs and ('name' in kwargs or 'id' in kwargs)) or ('instance' in kwargs)):
            return

        if 'parent_id' in kwargs:
            self.parent_id = kwargs['parent_id']
        else:
            self.parent_id = None

        if 'parent_link' in kwargs:
            self.parent_link = kwargs['parent_link']
        else:
            self.parent_link = None

        if 'form_index' in kwargs:
            self.form_index = kwargs['form_index']
        else:
            self.form_index = None

        if 'save' in kwargs:
            self.save = kwargs['save']
        else:
            self.save = False

        self._extended_table = None
        self.new_instance = None
        self.background_instances = []
        self.name_set = False

        oac = g_helper.get_org_access_control()

        if 'table_name' in kwargs:
            self._table_name = kwargs['table_name']

            if 'name' in kwargs:
                self.instance = oac.get_instance_data(kwargs['table_name'], {'name': [kwargs['name']]})[0]
                self.initialize_name(kwargs['name'])
            else:
                self.instance = oac.get_instance_data(kwargs['table_name'], {'id': [kwargs['id']]})[0]
                self.initialize_name(self.instance.name)
        else:
            self.instance = kwargs['instance']
            self._table_name = kwargs['instance'].__tablename__
            self.initialize_name(self.instance.name)

        self._table_data = oac.get_record(TableObject, {'name': self._table_name})
        self._history_table_data = oac.get_record(TableObject, {'name': 'history'})
        self._extended_table_data = None
        self.foreign_keys = {}
        self.foreign_keys_display = {}
        self.columns = self.set_columns()
        self.modified_columns = {}
        self.initialize_values()
        self.old_name = self.instance.name
        self.action_results = {}

    @property
    def table_data(self):
        return self._table_data

    @property
    def table_name(self):
        return self._table_name

    @property
    def instance_class(self):
        return self.instance.__class__

    @property
    def instance_name(self):
        return self.instance.name

    @property
    def instance_id(self):
        return self.instance.id

    def get_new_name(self):
        self.name_set = True
        if self._extended_table_data is not None:
            self.set_name(self._extended_table_data.get_new_name())
        else:
            self.set_name(self._table_data.get_new_name())

        for instance in self.background_instances:
            if instance.__tablename__ == 'history':
                instance.instance_name = self.instance.name

    def set_save_data(self):
        if not self.name_set:
            self.get_new_name()

        self.background_instances.append(self._history_table_data)
        self.background_instances.append(self._table_data)

    def commit(self):
        if self.instance.date_created is None and not self.new_instance:
            self.instance.instance.date_created = datetime.datetime.utcnow()
        elif not self.save:
            return False, {"page_msg": "Commit Error: instance data was not set to save"}

        self.set_save_data()
        oac = g_helper.get_org_access_control()
        commit_status, commit_msg = oac.save_data_instance([self.instance], self.background_instances)

        if commit_status:
            self.instance_id = commit_msg.items()[0]
            self.execute_actions()

        return commit_status, commit_msg

    def execute_actions(self, actions=None):
        oac = g_helper.get_org_access_control()

        if actions is None:
            if self.new_instance:
                actions = oac.get_table_object_actions(self._table_data.id, 'insert')
            else:
                actions = oac.get_table_object_actions(self._table_data.id, 'update')

        if actions is not None:
            for action in actions:
                if action.ActionTableObject.field_id is not None and \
                                action.ActionTableObject.field_id in self.modified_columns.keys():
                    status = action.execute_action(table_id=self._table_data.id,
                                                   field_id=action.ActionTableObject.field_id,
                                                   new_value=self.modified_columns[action.ActionTableObject.field_id],
                                                   instance_id=self.instance_id)
                else:
                    status = action.execute_action(table_id=self._table_data.id, field_id=None, new_value=None,
                                                   instance_id=self.instance_id)

                if status:
                    self.action_results.update(action.results.items())

    def set_values(self, field_values):
        for field_name, field_value in field_values.items():
            self.set_value(field_name, field_value)

    def set_value(self, field_name, field_value):
        exclude_list = ['id', 'last_modified', 'date_created']

        if self.columns[field_name].data_type.name.lower() == 'boolean':
            instance_value = bool(getattr(self.instance, field_name))
        else:
            instance_value = getattr(self.instance, field_name)

        if field_name in self.foreign_keys.keys() and field_value is not None:
            field_value = self.set_foreign_key_field_value(field_name, field_value)

        if (field_name not in exclude_list and
                ((instance_value is None and field_value is not None) or
                 (instance_value is not None and field_value is None) or field_value != instance_value) and
                ((field_name == 'name' and field_value is None and self.new_instance and self.save)
                 or (field_name != 'name'))):

            logging.info('table_name: ' + self.table_name + '    field_name: ' + field_name + "   field_value: " +
                         str(field_value) + " type: " +
                         str(type(field_value)) + "   getattr: " +
                         str(instance_value) + " type: " +
                         str(type(instance_value)))
            logging.info('self.instances[instance_name].new_instance: ' +
                         str(self.new_instance))
            logging.info('field_name not in exclude_list: ' + str(field_name not in exclude_list))
            logging.info('(instance_value is None and field_value is not None): ' + str(
                (instance_value is None and field_value is not None)))
            logging.info('(instance_value is not None and field_value is None): ' + str(
                (instance_value is not None and field_value is None)))
            logging.info('field_value != instance_value: ' + str(field_value != instance_value))
            logging.info('not (field_name == name and field_value is None and ' \
                         'self.instances[instance_name].new_instance): ' + \
                         str(not (field_name == 'name' and field_value is None and
                                  self.new_instance)))
            logging.info('saving data')
            logging.info('')

            self.save = True
            self.modified_columns[self.columns[field_name].id] = instance_value is None

            new_history = models.History()
            new_history.name = self._history_table_data.get_new_name()
            new_history.table_object_id = self._table_data.id
            new_history.field_id = self.columns[field_name].id
            new_history.organization_id = getattr(self.instance, 'organization_id')
            new_history.instance_name = self.instance_name
            new_history.old_value = getattr(self.instance, field_name, None)
            new_history.new_value = field_value
            new_history.user_id = g.user.id
            self.background_instances.append(new_history)

            setattr(self.instance, field_name, field_value)

    def set_columns(self):
        # http://docs.sqlalchemy.org/en/latest/core/metadata.html
        # http://docs.sqlalchemy.org/en/latest/core/reflection.html
        cols = {}
        for row in self._table_data.fields:
            cols[row.display_name] = row
            if row.fk_fields:
                self.foreign_keys[row.display_name] = row.fk_fields
            if row.fk_fields_display:
                self.foreign_keys_display[row.display_name] = row.fk_fields_display

        if self._table_data.extends_table_object_id:
            oac = g_helper.get_org_access_control()
            self._extended_table_data = oac.get_record(TableObject, {'id': self._table_data.extends_table_object_id})

            for row in self._extended_table_data.fields:
                cols[row.display_name] = row
                if row.fk_fields:
                    self.foreign_keys[row.display_name] = row.fk_fields
                if row.fk_fields_display:
                    self.foreign_keys_display[row.display_name] = row.fk_fields_display
                    
        return cols

    def initialize_name(self, instance_name):
        # logging.info('instance.instance.name: ' + str(self.instance.name))
        # logging.info('instance_name: ' + str(instance_name))
        # logging.info('self.table_name: ' + str(self.table_name))
        if self.instance.name is None or self.instance.name == '':
            self.new_instance = True
            self.instance.name = 'new'
        elif instance_name is not None and ('empty_row' in instance_name or 'new' in instance_name):
            self.new_instance = True
            self.instance.name = instance_name
        else:
            self.new_instance = False
            self.name_set = True

    def set_name(self, instance_name):
        self.instance.name = instance_name

    def set_parent_id(self, field, parent_id=None):
        self.parent_link = field
        if self.new_instance:
            setattr(self.instance, field, parent_id)
            self.parent_id = parent_id
        else:
            self.parent_id = getattr(self.instance, field)

    def initialize_values(self):
        # logging.info('instance.instance.name: ' + str(self.instance.name))

        if self.new_instance:
            for field, meta_data in self.columns.items():
                if self.parent_link == meta_data.display_name:
                    setattr(self.instance, meta_data.display_name, self.parent_id)
                elif meta_data.data_type_id == 3:
                    # default sets booleans to false rather than null
                    if meta_data.default is not None and (meta_data.default.lower == 'true' or
                                                          meta_data.default == '1' or
                                                          meta_data.default.lower == 'yes'):
                        setattr(self.instance, meta_data.display_name, True)
                    else:
                        setattr(self.instance, meta_data.display_name, False)
                elif meta_data.default is not None and meta_data.default != '':
                    if meta_data.default == 'user':
                        default = g.user.id
                    elif meta_data.data_type_id == 10 and meta_data.default == 'today':
                        default = datetime.date.today()
                    elif meta_data.data_type_id == 4 and meta_data.default == 'now':
                        default = datetime.datetime.utcnow().replace(microsecond=0)
                    elif meta_data.display_name == 'organization_id' and meta_data.default == 'org':
                        default = session['org_id']['current_org_id']
                    else:
                        default = meta_data.default

                    setattr(self.instance, meta_data.display_name, default)

        # logging.info('instance.instance.name: ' + str(self.instance.name))

    def set_organization_id(self, row_org_id = None):
        oac = g_helper.get_org_access_control()

        if row_org_id is not None:
            if isinstance(row_org_id, int):
                self.instance.organization_id = row_org_id
            else:
                org_record = oac.get_row('organization', {'name': row_org_id})

                if org_record:
                    self.instance.organization_id = org_record.id

        if oac.current_org_id is not None:
            self.instance.organization_id = oac.current_org_id
        else:
            self.instance.organization_id = 1

    def set_foreign_key_field_value(self, field_name, field_value):
        oac = g_helper.get_org_access_control()
        try:
            field_value = int(field_value)
            fk_record = oac.get_row(self.columns[field_name].fk_table_object.name, {'id': field_value})
            # crude error throwing for no record found
            fk_record.id
        except:
            if self.columns[field_name].fk_table_object.name == 'field':
                fk_record = oac.get_row(self.columns[field_name].fk_table_object.name,
                                        {self.foreign_keys[field_name].display_name: field_value,
                                         'table_object_id': self.columns[field_name].fk_table_object.id})
            elif self.columns[field_name].fk_table_object.name == 'select_list':
                fk_record = oac.get_row(self.columns[field_name].fk_table_object.name,
                                        {self.foreign_keys[field_name].display_name: field_value,
                                         'select_list_id': self.columns[field_name].select_list_id})
            elif field_name in self.foreign_keys_display:
                fk_record = oac.get_row(self.columns[field_name].fk_table_object.name,
                                        {self.foreign_keys_display[field_name].display_name: field_value})
            else:
                fk_record = oac.get_row(self.columns[field_name].fk_table_object.name,
                                        {self.foreign_keys[field_name].display_name: field_value})

        if fk_record:
            setattr(self.instance, field_name, fk_record.id)
            return fk_record.id
        else:
            setattr(self.instance, field_name, None)
            return None
