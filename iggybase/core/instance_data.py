from iggybase import g_helper
from iggybase import models
from iggybase.admin.models import TableObject
from flask import g, session
import datetime
from iggybase.core.constants import ActionType, DatabaseEvent
from iggybase.core.action import Action
from collections import OrderedDict
import operator
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

        self.oac = g_helper.get_org_access_control()

        if 'table_name' in kwargs:
            self._table_name = kwargs['table_name']

            if 'name' in kwargs:
                self.instance = self.oac.get_instance_data(kwargs['table_name'], {'name': [kwargs['name']]})[0]
                self.initialize_name(kwargs['name'])
            else:
                self.instance = self.oac.get_instance_data(kwargs['table_name'], {'id': [kwargs['id']]})[0]
                self.initialize_name(self.instance.name)
        else:
            self.instance = kwargs['instance']
            self._table_name = kwargs['instance'].__tablename__
            self.initialize_name(self.instance.name)

        self._table_data = self.oac.get_record(TableObject, {'name': self._table_name})
        self._history_table_data = None
        self.foreign_keys = {}
        self.foreign_keys_display = {}
        self.field_roles = {}
        self.columns = self.set_columns()
        self.modified_columns = {}
        self.initialize_values()
        self.instance_id = self.instance.id
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

    def get_new_name(self):
        self.name_set = True

        if self._table_data.extends_table_object_id is not None:
            self.set_name(self._table_data.extends_table.get_new_name())
        else:
            self.set_name(self._table_data.get_new_name())

        for instance in self.background_instances:
            if instance.__tablename__ == 'history':
                instance.instance_name = self.instance.name

    def set_save_data(self):
        if not self.name_set:
            self.get_new_name()

        self.background_instances.append(self._history_table_data)
        if self.new_instance:
            if self._table_data.extends_table is not None:
                self.background_instances.append(self._table_data.extends_table)
            else:
                self.background_instances.append(self._table_data)

    def commit(self):
        if not self.save:
            return False, {"page_msg": "Commit Error: instance data was not set to save"}

        if self.instance.date_created is None and not self.new_instance:
            self.instance.instance.date_created = datetime.datetime.utcnow()

        self.instance.instance.last_modified = datetime.datetime.utcnow()

        self.set_save_data()
        commit_status, commit_msg = self.oac.save_data_instance([self.instance], self.background_instances)

        if commit_status:
            self.instance_id = commit_msg.items()[0]
            self.execute_actions()

        return commit_status, commit_msg

    def execute_actions(self, actions=None):
        if actions is None:
            if self.new_instance:
                actions = Action(ActionType.TABLE, action_table=self.table_data.id, action_event=DatabaseEvent.INSERT)
            else:
                actions = Action(ActionType.TABLE, action_table=self.table_data.id, action_event=DatabaseEvent.UPDATE)

        if actions.actions:
            status = actions.execute_table_actions(self._table_data.id, self.modified_columns, self.instance_id)
            self.action_results = actions.results

    def field_display_name(self, field_name):
        if self.field_roles[field_name] and self.field_roles[field_name].display_name:
            return self.field_roles[field_name].display_name.replace("_", " ").title()
        elif self.columns[field_name].display_name:
            return self.columns[field_name].display_name.replace("_", " ").title()
        else:
            return 'WHOA! Something is not right here. There is no display name for field ' + field_name + "."

    def set_values(self, field_values):
        for field_name, field_value in field_values.items():
            self.set_value(field_name, field_value)

    def set_value(self, field_name, field_value):
        exclude_list = ['id', 'last_modified', 'date_created']

        instance_value = getattr(self.instance, field_name)

        if instance_value and self.columns[field_name].data_type.name.lower() == 'boolean':
            instance_value = bool(getattr(self.instance, field_name))
        elif instance_value and self.columns[field_name].data_type.name.lower() == 'integer':
            instance_value = int(getattr(self.instance, field_name))
        elif instance_value and (self.columns[field_name].data_type.name.lower() == 'float' or
                                         self.columns[field_name].data_type.name.lower() == 'decimal'):
            instance_value = float(getattr(self.instance, field_name))

        if field_name in self.foreign_keys.keys() and field_value is not None:
            field_value = self.set_foreign_key_field_value(field_name, field_value)

        if (field_name not in exclude_list and
                ((instance_value is None and field_value is not None) or
                 (instance_value is not None and field_value is None) or field_value != instance_value) and
                ((field_name == 'name' and field_value is None and self.new_instance)
                 or (field_name != 'name'))):

            if self._history_table_data is None:
                self._history_table_data = self.oac.get_record(TableObject, {'name': 'history'})

            self.save = True
            self.modified_columns[self.columns[field_name].id] = (instance_value, field_value)

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
        rac = g_helper.get_role_access_control()

        temp_cols = {}
        not_found = 99
        for row in self._table_data.fields:
            field_role = [role for role in row.field_roles if role.role_id == rac.role.id]
            if field_role:
                self.field_roles[row.display_name] = field_role[0]
                if field_role[0].order:
                    temp_cols[field_role[0].order] = row
                elif row.order:
                    temp_cols[row.order] = row
                else:
                    temp_cols[not_found] = row
                    not_found += 1
            else:
                self.field_roles[row.display_name] = None
                if row.order:
                    temp_cols[row.order] = row
                else:
                    temp_cols[not_found] = row
                    not_found += 1

            if row.fk_fields:
                self.foreign_keys[row.display_name] = row.fk_fields
                if row.fk_fields_display:
                    self.foreign_keys_display[row.display_name] = row.fk_fields_display
                else:
                    self.foreign_keys_display[row.display_name] = [f for f in row.fk_table_object.fields
                                                                   if f.display_name == 'name'][0]

        if self._table_data.extends_table_object_id:
            for row in self._table_data.extends_table.fields:
                field_role = [role for role in row.field_roles if role.role_id == rac.role.id]
                if field_role:
                    self.field_roles[row.display_name] = field_role[0]
                    if field_role[0].order:
                        temp_cols[field_role[0].order] = row
                    elif row.order:
                        temp_cols[row.order] = row
                    else:
                        temp_cols[not_found] = row
                        not_found += 1
                else:
                    self.field_roles[row.display_name] = None
                    if row.order:
                        temp_cols[row.order] = row
                    else:
                        temp_cols[not_found] = row
                        not_found += 1

                if row.fk_fields:
                    self.foreign_keys[row.display_name] = row.fk_fields
                    if row.fk_fields_display:
                        self.foreign_keys_display[row.display_name] = row.fk_fields_display
                    else:
                        self.foreign_keys_display[row.display_name] = [f for f in row.fk_table_object.fields
                                                                       if f.display_name == 'name'][0]

        cols = OrderedDict()
        if temp_cols:
            for key, row in sorted(temp_cols.items()):
                cols[row.display_name] = row

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

    def set_organization_id(self, row_org_id = None):
        if row_org_id is not None:
            if isinstance(row_org_id, int):
                self.instance.organization_id = row_org_id
            else:
                org_record = self.oac.get_row('organization', {'name': row_org_id})

                if org_record:
                    self.instance.organization_id = org_record.id

        if self.oac.current_org_id is not None:
            self.instance.organization_id = self.oac.current_org_id
        else:
            self.instance.organization_id = 1

    def set_foreign_key_field_value(self, field_name, field_value):
        try:
            field_value = int(field_value)
            fk_record = self.oac.get_row(self.columns[field_name].fk_table_object.name, {'id': field_value})
            # crude error throwing for no record found
            fk_record.id
        except:
            if self.columns[field_name].fk_table_object.name == 'field':
                fk_record = self.oac.get_row(self.columns[field_name].fk_table_object.name,
                                        {self.foreign_keys[field_name].display_name: field_value,
                                         'table_object_id': self.columns[field_name].fk_table_object.id})
            elif self.columns[field_name].fk_table_object.name == 'select_list':
                fk_record = self.oac.get_row(self.columns[field_name].fk_table_object.name,
                                        {self.foreign_keys[field_name].display_name: field_value,
                                         'select_list_id': self.columns[field_name].select_list_id})
            else:
                fk_record = self.oac.get_row(self.columns[field_name].fk_table_object.name,
                                        {self.foreign_keys_display[field_name].display_name: field_value})

        if fk_record:
            setattr(self.instance, field_name, fk_record.id)
            return fk_record.id
        else:
            setattr(self.instance, field_name, None)
            return None
