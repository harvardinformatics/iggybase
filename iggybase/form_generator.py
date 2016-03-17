from flask.ext.wtf import Form
from flask import g
from types import new_class
from iggybase.iggybase_form_fields import IggybaseBooleanField, IggybaseDateField, IggybaseFloatField,\
    IggybaseIntegerField, IggybaseLookUpField, IggybaseStringField, IggybaseTextAreaField, IggybaseSelectField,\
    IggybaseFileField, IggybasePasswordField
from wtforms import HiddenField
from wtforms.validators import DataRequired, Length, email, Optional
from iggybase.core.organization_access_control import OrganizationAccessControl
from iggybase.core.role_access_control import RoleAccessControl
from iggybase import constants
from json import dumps
import datetime
import logging


class FormGenerator():
    def __init__(self, table_object):
        self.organization_access_control = OrganizationAccessControl()
        self.role_access_control = RoleAccessControl()
        self.table_object = table_object
        self.classattr = {}
        self.table_data = None

    def input_field(self, field_data, row_name, control_id, control_type, value=None):
        kwargs = {}
        validators = []

        if value is not None:
            kwargs['default'] = value

        # no validators or classes attached to hidden fields, as it could cause issues
        # e.g. an empty hidden required field
        if field_data.FieldRole.visible != constants.VISIBLE:
            return HiddenField(field_data.FieldRole.display_name, **kwargs)

        if field_data.FieldRole.required == constants.REQUIRED:
            validators.append(DataRequired())
        else:
            validators.append(Optional())

        if field_data.Field.length is not None and field_data.Field.data_type_id == constants.STRING:
            validators.append(Length(0, field_data.Field.length))

        if "email" in field_data.Field.field_name:
            validators.append(email())

        kwargs['validators'] = validators

        if field_data.Field.field_class is not None:
            kwargs['iggybase_class'] = control_type + ' ' + field_data.Field.field_class
        else:
            kwargs['iggybase_class'] = control_type

        if ((field_data.FieldRole.permission_id == constants.DEFAULTED and row_name != 'new') or
                (field_data.FieldRole.permission_id == constants.IMMUTABLE and row_name == 'new') or
                (field_data.FieldRole.permission_id == constants.READ_WRITE)):
            kwargs['readonly'] = False
        else:
            kwargs['readonly'] = True

        if field_data.Field.foreign_key_table_object_id is not None:
            long_text = self.role_access_control.has_access("TableObject", {'name': 'long_text'})
            if long_text.id == field_data.Field.foreign_key_table_object_id:
                if value is not None:
                    lt_row = self.organization_access_control.get_long_text(value)
                    kwargs['default'] = lt_row.long_text

                return IggybaseTextAreaField(field_data.FieldRole.display_name, **kwargs)
            else:
                choices = self.organization_access_control.\
                    get_foreign_key_data(field_data.Field.foreign_key_table_object_id)

                if len(choices) > 25:
                    kwargs['iggybase_class'] = control_type

                    if value is not None:
                        value = self.organization_access_control.\
                            get_foreign_key_data(field_data.Field.foreign_key_table_object_id, {'id': value})
                        kwargs['default'] = value[1][1]

                    return IggybaseLookUpField(field_data.FieldRole.display_name, **kwargs)
                else:
                    kwargs['coerce'] = int
                    kwargs['choices'] = choices

                    return IggybaseSelectField(field_data.FieldRole.display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.INTEGER:
            return IggybaseIntegerField(field_data.FieldRole.display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.FLOAT:
            return IggybaseFloatField(field_data.FieldRole.display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.BOOLEAN:
            self.classattr['bool_' + control_id]=HiddenField('bool_' + control_id, default=value)
            return IggybaseBooleanField(field_data.FieldRole.display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.DATE:
            return IggybaseDateField(field_data.FieldRole.display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.PASSWORD:
            return IggybasePasswordField(field_data.FieldRole.display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.FILE:
            return IggybaseFileField(field_data.FieldRole.display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.TEXT_AREA:
            return IggybaseTextAreaField(field_data.FieldRole.display_name, **kwargs)
        else:
            return IggybaseStringField(field_data.FieldRole.display_name, **kwargs)

    def empty_form(self):
        newclass = new_class('DynamicForm', (Form,))

        return newclass()

    def default_single_entry_form(self, table_data, row_name='new'):
        self.table_data = table_data

        self.classattr = self.row_fields(1, row_name)

        fields = self.role_access_control.fields(self.table_data.id)

        self.classattr['startmaintable_'+str(self.table_data.id)]=\
            HiddenField('startmaintable_'+str(self.table_data.id), default=self.table_data.name)

        self.get_row(fields, row_name, 1)

        newclass = new_class('DynamicForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        return newclass()

    def default_multiple_entry_form(self, row_names=[]):
        self.table_data = self.role_access_control.has_access('TableObject', {'name': self.table_object})

        fields = self.role_access_control.fields(self.table_data.id)

        self.classattr['startmaintable_'+str(self.table_data.id)]=\
            HiddenField('startmaintable_'+str(self.table_data.id), default=self.table_data.name)

        row_counter = 1
        for row_name in row_names:
            self.classattr.update(self.row_fields(row_counter, row_name))
            self.get_row(fields, row_name, row_counter, 'table-control')
            row_counter += 1

        newclass = new_class('DynamicForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        return newclass()

    def default_parent_child_form(self, table_data, child_tables, link_data, row_name='new'):
        self.table_data = table_data

        self.classattr = self.row_fields(1, row_name)

        self.classattr['startmaintable_'+str(self.table_data.id)]=\
            HiddenField('startmaintable_'+str(self.table_data.id), default=self.table_data.name)

        fields = self.role_access_control.fields(self.table_data.id)
        self.get_row(fields, row_name, 1)

        parent_id = self.organization_access_control.get_row_id(table_data.name, {'name': row_name})

        row_counter = 2
        child_index = 0
        for child_table in child_tables:
            self.table_data = child_table
            fields = self.role_access_control.fields(self.table_data.id)

            child_row_names = self.organization_access_control.get_child_row_names(child_table.name,
                                                                                   link_data[child_index].child_link_field_id,
                                                                                   parent_id)

            link_field = self.role_access_control.has_access('Field',
                                                             {'id': link_data[child_index].child_link_field_id})

            self.classattr['linkcolumn_'+str(child_table.id)]=\
                HiddenField('linkcolumn_'+str(child_table.id), default=link_field.field_name)

            self.classattr['startchildtable_'+str(child_table.id)]=\
                HiddenField('startchildtable_'+str(child_table.id), default=child_table.name)

            self.classattr['headers_'+str(child_table.id)]=\
                HiddenField('headers_'+str(child_table.id), default=self.get_field_headers(fields))

            if len(child_row_names) == 0:
                child_row_names.append('new')

            for child_row_name in child_row_names:
                #   needed to prevent oevrlapping row ids if rows are added dynamically
                child_row = (child_index * 1000) + row_counter

                self.classattr.update(self.row_fields(child_row, child_row_name))
                self.get_row(fields, child_row_name, child_row, 'table-control')
                row_counter += 1

            self.classattr['endchildtable_'+str(child_table.id)]=\
                HiddenField('endchildtable_'+str(child_table.id))

            child_index += 1

        newclass = new_class('DynamicForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        return newclass()

    def row_fields(self, row_count, row_name):
        table_id_field = HiddenField('table_id_'+str(row_count), default=self.table_data.id)
        table_name_field = HiddenField('table_name_'+str(row_count), default=self.table_data.name)
        row_field = HiddenField('row_name_'+str(row_count), default=row_name)

        return {'record_data_row_name_'+str(row_count): row_field,
                'record_data_table_name_'+str(row_count): table_name_field,
                'record_data_table_id_'+str(row_count): table_id_field}

    def get_row(self, fields, row_name, row_counter, control_type='data-control'):
        if row_name != 'new':
            data = self.organization_access_control.get_entry_data(self.table_data.name, {'name': str(row_name)})
            if data:
                data = data[0]

                if type(data) is list:
                    data = None
                    row_name = 'new'

        for field in fields:
            # logging.info(str(field.Field.id) + " " + field.Field.field_name +': ' + field.FieldRole.display_name)
            value = None
            if row_name != 'new' and data is not None:
                if  field.FieldRole.display_name in data.keys():
                    value = data[data.keys().index(field.FieldRole.display_name)]

            if value is None:
                self.classattr['old_value_'+field.Field.field_name+"_"+str(row_counter)]=\
                    HiddenField('old_value_'+field.Field.field_name+"_"+str(row_counter))
            else:
                self.classattr['old_value_'+field.Field.field_name+"_"+str(row_counter)]=\
                    HiddenField('old_value_'+field.Field.field_name+"_"+str(row_counter), default=value)

            if value is None and row_name == 'new' and (field.Field.default is not None and field.Field.default != ''):
                if field.Field.default == 'now':
                    value = datetime.datetime.utcnow()
                elif field.Field.default == 'user':
                    value = g.user.id
                elif field.Field.default is not None:
                    value = field.Field.default

            control_id = 'data_entry_' + field.Field.field_name+"_"+str(row_counter)
            self.classattr[control_id] = self.input_field(field, row_name, control_id, control_type, value)

        self.classattr['endrow_'+str(row_counter)]=\
            HiddenField('endrow_'+str(row_counter))

    def get_field_headers(self, fields):
        headers = ''
        for field in fields:
            if field.FieldRole.visible == 1:
                headers += field.FieldRole.display_name + '|'

        return dumps(headers[:-1])
