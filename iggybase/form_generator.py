from flask.ext.wtf import Form
from types import new_class
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SelectField, ValidationError, DateField, \
    HiddenField, FileField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, email
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
from iggybase.mod_auth.role_access_control import RoleAccessControl
from iggybase import constants
import logging


class ReadonlyStringField(StringField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyStringField, self).__call__(*args, **kwargs)


class ReadonlyIntegerField(IntegerField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyIntegerField, self).__call__(*args, **kwargs)


class ReadonlyFloatField(FloatField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyFloatField, self).__call__(*args, **kwargs)


class ReadonlyBooleanField(BooleanField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyBooleanField, self).__call__(*args, **kwargs)


class ReadonlyTextAreaField(TextAreaField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyTextAreaField, self).__call__(*args, **kwargs)


class DateFieldClass(DateField):
    def __call__(self, *args, **kwargs):
        kwargs['class'] = 'form-control datepicker-field'
        return super(DateFieldClass, self).__call__(*args, **kwargs)


class ReadonlyDateField(DateField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyDateField, self).__call__(*args, **kwargs)


class LookUpField(StringField):
    def __call__(self, *args, **kwargs):
        kwargs['class'] = 'form-control lookupfield form-control-lookup'
        return \
            super(LookUpField, self).__call__(*args, **kwargs)


class FormGenerator():
    def __init__(self, module, table_object):
        self.organization_access_control = OrganizationAccessControl()
        self.role_access_control = RoleAccessControl()
        self.table_object = table_object
        self.module = module
        self.classattr = {}
        self.table_data = None

    def input_field(self, field_data, value=None):
        validators = []
        if field_data.FieldRole.required == constants.REQUIRED:
            validators.append(DataRequired())

        if field_data.Field.length is not None and field_data.Field.data_type_id == constants.STRING:
            validators.append(Length(0, field_data.Field.length))

        if "email" in field_data.Field.field_name:
            validators.append(email())

        if field_data.FieldRole.visible != constants.VISIBLE:
            if value is not None:
                wtf_field = HiddenField(field_data.FieldRole.display_name, default=value)
            else:
                wtf_field = HiddenField(field_data.FieldRole.display_name)
        else:
            if field_data.FieldRole.permission_id == constants.READ_WRITE:
                if field_data.Field.foreign_key_table_object_id is not None:
                    long_text = self.role_access_control.has_access("TableObject", {'name': 'long_text'})
                    if long_text.id == field_data.Field.foreign_key_table_object_id:
                        if value is not None:
                            lt_row = self.organization_access_control.get_long_text(value)
                            value = lt_row.long_text

                            wtf_field = TextAreaField(field_data.FieldRole.display_name, validators, default=value)
                        else:
                            wtf_field = TextAreaField(field_data.FieldRole.display_name, validators)
                    else:
                        choices = self.organization_access_control. \
                            get_foreign_key_data(field_data.Field.foreign_key_table_object_id)

                        if len(choices) > 25:
                            if value is not None:
                                wtf_field = LookUpField(field_data.FieldRole.display_name, validators,
                                                        default=[item[1] for item in choices if item[0] == value][0])
                            else:
                                wtf_field = LookUpField(field_data.FieldRole.display_name, validators)
                        else:
                            if value is not None:
                                wtf_field = SelectField(field_data.FieldRole.display_name, validators, coerce=int, \
                                                        choices=choices, default=value)
                            else:
                                wtf_field = SelectField(field_data.FieldRole.display_name, validators, coerce=int, \
                                                        choices=choices)
                else:
                    kwargs = {'validators': validators}
                    if field_data.Field.data_type_id == constants.INTEGER:
                        wtf_class = IntegerField
                    elif field_data.Field.data_type_id == constants.FLOAT:
                        wtf_class = FloatField
                    elif field_data.Field.data_type_id == constants.BOOLEAN:
                        wtf_class = BooleanField
                    elif field_data.Field.data_type_id == constants.DATE:
                        wtf_class = DateFieldClass
                    elif field_data.Field.data_type_id == constants.PASSWORD:
                        wtf_class = PasswordField
                    elif field_data.Field.data_type_id == constants.FILE:
                        wtf_class = FileField
                    elif field_data.Field.data_type_id == constants.TEXT_AREA:
                        wtf_class = TextAreaField
                    else:
                        wtf_class = StringField

                    if value is not None:
                        kwargs['default'] = value

                    wtf_field = wtf_class(field_data.FieldRole.display_name, **kwargs)
            else:
                kwargs = {'validators': validators}
                if field_data.Field.foreign_key_table_object_id is not None:
                    long_text = self.role_access_control.has_access("TableObject", {'name': 'long_text'})
                    if long_text.id == field_data.Field.foreign_key_table_object_id:
                        if value is not None:
                            lt_row = self.organization_access_control.get_long_text(value)
                            value = lt_row.long_text

                        wtf_class = TextAreaField
                    else:
                        if value is not None:
                            choices = self.organization_access_control. \
                                get_foreign_key_data(field_data.Field.foreign_key_table_object_id)
                            value = [item[1] for item in choices if item[0] == value]

                        wtf_class = ReadonlyStringField
                elif field_data.Field.data_type_id == constants.INTEGER:
                    wtf_class = ReadonlyIntegerField
                elif field_data.Field.data_type_id == constants.FLOAT:
                    wtf_class = ReadonlyFloatField
                elif field_data.Field.data_type_id == constants.BOOLEAN:
                    wtf_class = ReadonlyBooleanField
                elif field_data.Field.data_type_id == constants.DATE:
                    wtf_class = ReadonlyDateField
                elif field_data.Field.data_type_id == constants.TEXT_AREA:
                    wtf_class = ReadonlyTextAreaField
                else:
                    wtf_class = ReadonlyStringField

                if value is not None:
                    kwargs['default'] = value

                wtf_field = wtf_class(field_data.FieldRole.display_name, **kwargs)

        return wtf_field

    def default_single_entry_form(self, table_data, row_name='new'):
        self.table_data = table_data

        self.classattr = self.hidden_fields('single')
        self.classattr.update(self.row_fields(1, row_name))

        fields = self.role_access_control.fields(self.table_data.id)

        self.classattr['hidden_startmaintable_'+str(self.table_data.id)]=\
            HiddenField('hidden_startmaintable_'+str(self.table_data.id), default=self.table_data.name)

        self.get_row(fields, row_name, 1)

        newclass = new_class('DynamicForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        return newclass()

    def default_multiple_entry_form(self, row_names=[]):
        self.table_data = self.role_access_control.has_access('TableObject', {'name': self.table_object})

        fields = self.role_access_control.fields(self.table_data.id)

        self.classattr = self.hidden_fields('multiple')

        self.classattr['hidden_startmaintable_'+str(self.table_data.id)]=\
            HiddenField('hidden_startmaintable_'+str(self.table_data.id), default=self.table_data.name)

        row_counter = 1
        for row_name in row_names:
            self.classattr.update(self.row_fields(row_counter, row_name))
            self.get_row(fields, row_name, row_counter)
            row_counter += 1

        newclass = new_class('DynamicForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        return newclass()

    def default_parent_child_form(self, table_data, child_tables, link_data, row_name='new'):
        self.table_data = table_data

        self.classattr = self.hidden_fields('parent_child')
        self.classattr.update(self.row_fields(1, row_name))

        self.classattr['hidden_startmaintable_'+str(self.table_data.id)]=\
            HiddenField('hidden_startmaintable_'+str(self.table_data.id), default=self.table_data.name)

        fields = self.role_access_control.fields(self.table_data.id)
        parent_id = self.get_row(fields, row_name, 1)

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
            self.classattr['hidden_linkcolumn_'+str(child_table.id)]=\
                HiddenField('hidden_linkcolumn_'+str(child_table.id), default=link_field.field_name)

            self.classattr['hidden_startchildtable_'+str(child_table.id)]=\
                HiddenField('hidden_startchildtable_'+str(child_table.id), default=child_table.name)


            for child_row_name in child_row_names:
                self.classattr.update(self.row_fields(row_counter, child_row_name, 'child_'))
                self.get_row(fields, child_row_name, row_counter, 'child_')
                row_counter += 1

            self.classattr['hidden_endchildtable_'+str(child_table.id)]=\
                HiddenField('hidden_endchildtable_'+str(child_table.id))

            child_index += 1

        newclass = new_class('DynamicForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        return newclass()

    def hidden_fields(self, form_type):
        module_field = HiddenField('module_0', default=self.module)
        table_field = HiddenField('table_object_0', default=self.table_object)
        entry_field = HiddenField('entry_0', default=form_type)

        return {'module_0': module_field, 'table_object_0': table_field, 'entry_0': entry_field}

    def row_fields(self, row_count, row_name, prefix = ''):
        table_id_field = HiddenField(prefix + 'table_id_'+str(row_count), default=self.table_data.id)
        table_name_field = HiddenField(prefix + 'table_name_'+str(row_count), default=self.table_data.name)
        row_field = HiddenField(prefix + 'row_name_'+str(row_count), default=row_name)

        return {'hidden_row_name_'+str(row_count): row_field,
                'hidden_table_name_'+str(row_count): table_name_field,
                'hidden_table_id_'+str(row_count): table_id_field}

    def get_row(self, fields, row_name, row_counter, prefix = ''):
        id = None

        if row_name != 'new':
            data = self.organization_access_control.get_entry_data(self.table_data.name, row_name)
            if data:
                data = data[0]

                if type(data) is list:
                    data = None
                    row_name = 'new'
                else:
                    id = data[data.keys().index('id')]

        for field in fields:
            value = None
            if row_name != 'new' and data is not None:
                if  field.FieldRole.display_name in data.keys():
                    value = data[data.keys().index(field.FieldRole.display_name)]

            if value is None:
                self.classattr['hidden_'+field.Field.field_name+"_"+str(row_counter)]=\
                    HiddenField('hidden_'+field.Field.field_name+"_"+str(row_counter))
            else:
                self.classattr['hidden_'+field.Field.field_name+"_"+str(row_counter)]=\
                    HiddenField('hidden_'+field.Field.field_name+"_"+str(row_counter), default=value)

            self.classattr[prefix + field.Field.field_name+"_"+str(row_counter)] = self.input_field(field, value)

        self.classattr['hidden_endrow_'+str(row_counter)]=\
            HiddenField('hidden_endrow_'+str(row_counter))

        return id