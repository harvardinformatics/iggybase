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
from json import dumps, loads
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
            # logging.info('input_field value: ' + str(value))
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
        newclass = new_class('EmptyForm', (Form,))

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

        newclass = new_class('MultipleForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        # tmp = newclass()
        # for field in tmp:
        #     logging.info(field.id +": "+str(field.data))

        return newclass()

    def default_single_entry_form(self, table_data, row_name='new'):
        self.table_data = table_data

        self.classattr = self.row_fields(1, row_name)

        fields = self.role_access_control.fields(self.table_data.id)

        self.classattr['startmaintable_'+str(self.table_data.id)]=\
            HiddenField('startmaintable_'+str(self.table_data.id), default=self.table_data.name)

        table_index = 0
        row_counter = 1
        self.get_row(fields, row_name, row_counter, 'data-control')

        if row_name != 'new':
            link_data, child_tables = self.role_access_control.get_child_tables(self.table_data.id)

            if child_tables:
                table_index, row_counter = self.linked_data(constants.CHILD_TABLES, child_tables, link_data,
                                                            table_index, row_name, row_counter)

            link_data, many_tables = self.role_access_control.get_many_tables(self.table_data.id)

            if many_tables:
                table_index, row_counter = self.child_data_form(constants.MANY_TO_MANY_TABLES, many_tables, link_data,
                                                                table_index, row_name, row_counter)

        newclass = new_class('SingleForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        return newclass()

    def linked_data(self, link_type, link_tables, link_data, table_index, row_name, row_counter):
        parent_id = self.organization_access_control.get_row_id(self.table_data.name, {'name': row_name})

        for link_table in link_tables:
            table_index_adj = table_index * 1000

            self.table_data = link_table
            fields = self.role_access_control.fields(self.table_data.id)

            if link_type == constants.CHILD_TABLES:
                row_names = self.organization_access_control.get_many_row_names(link_table.name,
                                                                                link_data[table_index].link_field_id,
                                                                                parent_id)
            elif link_type == constants.MANY_TO_MANY_TABLES:
                pass
            elif link_type == constants.GRANDCHILD_TABLES:
                pass
            else:
                return

            link_field = self.role_access_control.has_access('Field',
                                                             {'id': link_data[table_index].child_link_field_id})

            self.classattr['linkcolumn_'+str(link_table.id)]=\
                HiddenField('linkcolumn_'+str(link_table.id), default=link_field.field_name)

            self.classattr['startchildtable_'+str(link_table.id)]=\
                HiddenField('startchildtable_'+str(link_table.id), default=link_table.name)

            self.classattr['headers_'+str(link_table.id)]=\
                HiddenField('headers_'+str(link_table.id), default=self.get_field_headers(fields))

            if len(row_names) == 0:
                row_names.append('new')

            for row_name in row_names:
                #   needed to prevent oevrlapping row ids if rows are added dynamically
                link_row =  table_index_adj + row_counter

                self.classattr.update(self.row_fields(link_row, row_name))
                self.get_row(fields, row_name, link_row, 'table-control')
                row_counter += 1

            self.classattr['endchildtable_'+str(link_table.id)]=\
                HiddenField('endchildtable_'+str(link_table.id))

            table_index += 1

        return table_index, row_counter

    def row_fields(self, row_count, row_name):
        table_id_field = HiddenField('table_id_'+str(row_count), default=self.table_data.id)
        table_name_field = HiddenField('table_name_'+str(row_count), default=self.table_data.name)
        row_field = HiddenField('row_name_'+str(row_count), default=row_name)

        return {'record_data_row_name_'+str(row_count): row_field,
                'record_data_table_name_'+str(row_count): table_name_field,
                'record_data_table_id_'+str(row_count): table_id_field}

    def get_row(self, fields, row_name, row_counter, control_type):
        # logging.info('row_name: ' + row_name)
        if row_name != 'new':
            data = self.organization_access_control.get_entry_data(self.table_data.name, {'name': str(row_name)})
            if data:
                data = data[0]

                if type(data) is list:
                    # logging.info('data is none')
                    data = None
                    row_name = 'new'

        for field in fields:
            # logging.info(str(field.Field.id) + " " + field.Field.field_name +': ' + field.FieldRole.display_name)
            value = None
            if row_name != 'new' and data is not None:
                if  field.FieldRole.display_name in data.keys():
                    value = data[data.keys().index(field.FieldRole.display_name)]

            if value is None:
                # logging.info(field.Field.field_name+': None')
                self.classattr['old_value_'+field.Field.field_name+"_"+str(row_counter)]=\
                    HiddenField('old_value_'+field.Field.field_name+"_"+str(row_counter))

                if row_name == 'new' and (field.Field.default is not None and field.Field.default != ''):
                    # logging.info(field.Field.field_name + ': setting default')
                    if field.Field.default == 'now':
                        value = datetime.datetime.utcnow()
                    elif field.Field.default == 'user':
                        value = g.user.id
                    elif field.Field.default is not None:
                        value = field.Field.default
            else:
                # logging.info(field.Field.field_name+': '+str(value))
                self.classattr['old_value_'+field.Field.field_name+"_"+str(row_counter)]=\
                    HiddenField('old_value_'+field.Field.field_name+"_"+str(row_counter), default=value)

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
