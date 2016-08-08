from flask.ext.wtf import Form
from flask import g
from types import new_class
from iggybase.iggybase_form_fields import IggybaseBooleanField, IggybaseDateField, IggybaseFloatField,\
    IggybaseIntegerField, IggybaseLookUpField, IggybaseStringField, IggybaseTextAreaField, IggybaseSelectField,\
    IggybaseFileField, IggybasePasswordField
from wtforms import HiddenField
from wtforms.validators import DataRequired, Length, email, Optional
from iggybase import g_helper
from iggybase import constants
from iggybase.core.field_collection import FieldCollection
from iggybase.core.data_instance import DataInstance
from json import dumps, loads
<<<<<<< Updated upstream
import datetime, time
=======
import datetime
>>>>>>> Stashed changes
import logging


class FormGenerator():
    def __init__(self, table_name):
        self.organization_access_control = g_helper.get_org_access_control()
        self.role_access_control = g_helper.get_role_access_control()
        self.table_name = table_name
        self.classattr = {}
        self.table_meta_data = None
        self.dropdowns = {}

    def input_field(self, field_data, display_name, row_name, control_id, control_type, value=None):
        kwargs = {}
        validators = []
        if value is not None:
            # logging.info('input_field value: ' + str(value))
            kwargs['default'] = value

        # no validators or classes attached to hidden fields, as it could cause issues
        # e.g. an empty hidden required field
        if field_data.FieldRole.visible != constants.VISIBLE:
            return HiddenField(field_data.FieldRole.display_name, **kwargs)

        if field_data.Field.description != "":
            kwargs['title'] = field_data.Field.description

        if field_data.FieldRole.required == constants.REQUIRED:
            validators.append(DataRequired())
        else:
            validators.append(Optional())

        if field_data.Field.length is not None and field_data.Field.data_type_id == constants.STRING:
            validators.append(Length(0, field_data.Field.length))

        if "email" in field_data.Field.display_name:
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

        if field_data.Field.select_list_id is not None:
            choices = self.organization_access_control.get_select_list(field_data.Field.select_list_id)

            kwargs['coerce'] = int
            kwargs['choices'] = choices

            return IggybaseSelectField(display_name, **kwargs)
        elif field_data.is_foreign_key:
            long_text = self.role_access_control.has_access("TableObject", {'name': 'long_text'})

            if long_text.id == field_data.FK_TableObject.id:
                if value is not None:
                    lt_row = self.organization_access_control.get_long_text(value)
                    kwargs['default'] = lt_row.long_text
                    self.classattr['long_text_' + control_id] = HiddenField('long_text_' + control_id, default=value)
                else:
                    self.classattr['long_text_' + control_id] = HiddenField('long_text_' + control_id)

                return IggybaseTextAreaField(display_name, **kwargs)
            else:
                if field_data.name not in self.dropdowns:
                    self.dropdowns[field_data.name] = self.organization_access_control.\
                        get_foreign_key_data(field_data.FK_TableObject, field_data.FK_Field)

                choices = self.dropdowns[field_data.name]

                if field_data.Field.drop_down_list_limit:
                    drop_down_limit = field_data.Field.drop_down_list_limit
                else:
                    drop_down_limit = 25

                if len(choices) > drop_down_limit:
                    kwargs['iggybase_class'] = control_type

                    if value is not None:
                        value = [item for item in choices if item[0] == value]

                        if len(value) > 0:
                            kwargs['default'] = value[0][1]

                    return IggybaseLookUpField(display_name, **kwargs)
                else:
                    # logging.info(display_name + ' value: ' + str(value))
                    kwargs['coerce'] = int
                    kwargs['choices'] = choices

                    if value is not None:
                        kwargs['default'] = value

                    return IggybaseSelectField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.INTEGER:
            return IggybaseIntegerField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.FLOAT:
            return IggybaseFloatField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.BOOLEAN:
            self.classattr['bool_' + control_id]=HiddenField('bool_' + control_id, default=value)
            return IggybaseBooleanField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.DATE:
            return IggybaseDateField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.PASSWORD:
            return IggybasePasswordField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.FILE:
            return IggybaseFileField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.TEXT_AREA:
            return IggybaseTextAreaField(display_name, **kwargs)
        else:
            return IggybaseStringField(display_name, **kwargs)

    def empty_form(self):
        newclass = new_class('EmptyForm', (Form,))

        return newclass()

    def default_multiple_entry_form(self, row_names=[]):
<<<<<<< Updated upstream
        self.table_meta_data = self.role_access_control.has_access('TableObject', {'name': self.table_name})
        data_instance = DataInstance(self.table_meta_data.name, self.organization_access_control)

        self.classattr['startmaintable_'+str(self.table_meta_data.id)]=\
            HiddenField('startmaintable_'+str(self.table_meta_data.id), default=self.table_meta_data.name)
=======
        self.table_data = self.role_access_control.has_access('TableObject', {'name': self.table_object})
        data_instance = DataInstance(self.table_data.name, self.organization_access_control)

        fields = FieldCollection(None, self.table_data.name)
        fields.set_fk_fields()
        fields.set_defaults()

        self.classattr['startmaintable_'+str(self.table_data.id)]=\
            HiddenField('startmaintable_'+str(self.table_data.id), default=self.table_data.name)
>>>>>>> Stashed changes

        row_counter = 1
        for row_name in row_names:
            self.classattr.update(self.row_fields(row_counter, row_name))
<<<<<<< Updated upstream
            data_instance.get_data(row_name)
            self.get_row(data_instance, row_name, row_counter, 'table-control', data_instance, row_counter)
=======
            self.get_row(fields, row_name, row_counter, 'table-control', data_instance)
>>>>>>> Stashed changes
            row_counter += 1

        newclass = new_class('MultipleForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        return newclass()

<<<<<<< Updated upstream
    def default_data_entry_form(self, row_name='new', depth = 2):
        # start_time = time.time()
        # logging.info('default_data_entry_form start time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
=======
    def default_data_entry_form(self, table_data, row_name='new', depth = 2):
        logging.info('start time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        self.table_data = table_data
        data_instance = DataInstance(self.table_data.name, self.organization_access_control)

        self.classattr = self.row_fields(1, row_name)
>>>>>>> Stashed changes

        data_instance = DataInstance(self.table_name, row_name)

        # logging.info(self.table_name + ': ' + row_name)
        # logging.info(data_instance.instances[self.table_name])

<<<<<<< Updated upstream
        if row_name != 'new':
            data_instance.get_linked_instances(depth)

        self.get_table(data_instance, 'default')
=======
        parent_id = self.get_row(fields, row_name, 1, 'data-control', data_instance)

        self.classattr['endtable_'+str(self.table_data.id)]=\
            HiddenField('endtable_'+str(self.table_data.id), default=self.table_data.name)

        row_counter = 2
        if row_name != 'new':

            row_counter = self.linked_data(link_tables, link_data, row_name, row_counter, depth, [parent_id])
>>>>>>> Stashed changes

        self.classattr['form_data_table_0'] = \
            HiddenField('form_data_table_0', default=self.table_name)

<<<<<<< Updated upstream
        self.classattr['form_data_row_name_0'] = \
            HiddenField('form_data_row_name_0', default=row_name)

        self.classattr['row_counter'] = HiddenField('row_counter', default=data_instance.instance_counter)

        newclass = new_class('SingleForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        # logging.info('default_data_entry_form time: ' + str(time.time() - start_time))

        # logging.info('self.dropdowns')
        # logging.info(self.dropdowns)
        #logging.info('end time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        return newclass()

    def get_table(self, data_instance, form_type):
        row_counter = 0
        level = 0

        for table_name, table_data in data_instance.tables.items():
            # start_time = time.time()
            #logging.info('get_table loop table_name: ' + table_name)
            # logging.info(data_instance.instances[table_name])

            if table_data['link_data'] is not None:
                link_field = self.role_access_control. \
                    has_access('Field',
                               {'id': table_data['link_data'].child_link_field_id})
=======
        newclass = new_class('SingleForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        logging.info('end time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        return newclass()

    def linked_data(self, tables, table_data, row_name, row_counter, depth, parent_ids = [], current_depth = 0):
        parent_name = self.table_data.name

        for link_type, link_tables in tables.items():
            table_index = 0

            for link_table in link_tables:
                self.table_data = link_table

                fields = FieldCollection(None, self.table_data.name)
                fields.set_fk_fields()
                # default parent fk to parent id
                fk_defaults = {parent_name: parent_ids[0]}
                fields.set_defaults(fk_defaults)

                data_instance = DataInstance(self.table_data.name, self.organization_access_control, fields)

                child_data = None
                if link_type == 'child':
                    if current_depth == 0:
                        self.classattr['startchildtable_'+str(link_table.id)]=\
                            HiddenField('startchildtable_'+str(link_table.id), default=link_table.name)
                    else:
                        self.classattr['startgrandchildtable_'+str(link_table.id)]=\
                            HiddenField('startgrandchildtable_'+str(link_table.id), default=link_table.name)

                    # logging.info(link_table.name + ' ids:')
                    # logging.info(ids)

                    row_names = self.organization_access_control.\
                        get_child_row_names(link_table.name,
                                            table_data[link_type][table_index].child_link_field_id, parent_ids)

                    child_data, child_tables = self.role_access_control.get_link_tables(self.table_data.id, True)
                elif link_type == 'many' and current_depth == 0:
                    row_names = self.organization_access_control.\
                        get_many_row_names(link_table.name,
                                           table_data[link_type][table_index].link_table_object_id,
                                           parent_ids)
>>>>>>> Stashed changes

                self.classattr['linkcolumn_' + str(table_data['table_meta_data'].id)] = \
                    HiddenField('linkcolumn_' + str(table_data['table_meta_data'].id),
                                default=link_field.display_name)

            self.classattr['table_level_' + str(table_data['table_meta_data'].id)] = \
                HiddenField('table_level_' + str(table_data['table_meta_data'].id), default=table_data['level'])

            if level < table_data['level']:
                level = table_data['level']

            self.classattr['table_name_' + str(table_data['table_meta_data'].id)] = \
                HiddenField('table_name_' + str(table_data['table_meta_data'].id),
                            default=table_data['table_meta_data'].name)

<<<<<<< Updated upstream
            if table_data['level'] == 0 and form_type == 'default':
                control_type = 'data-control'
            else:
                control_type = 'table-control'

            for instance_name, instance in data_instance.instances[table_name].items():
                # logging.info(str(instance.id) + ' start time: ' +
                #              datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

                self.classattr.update(self.row_fields(row_counter, instance_name, table_data['table_meta_data']))
                self.get_row(data_instance, table_name, instance, control_type, row_counter)
=======
                if len(row_names) == 0:
                    row_names[0] = 'new'

                for row_id, data in row_names.items():
                    logging.info(str(row_id) + ' start time: ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

                    row_name = data[0]

                    self.classattr.update(self.row_fields(row_counter, row_name))
                    self.get_row(fields, row_name, row_counter, 'table-control', data_instance)
>>>>>>> Stashed changes

                row_counter += 1

            self.classattr['end_table_' + str(table_data['table_meta_data'].id)] = \
                HiddenField('end_table_' + str(table_data['table_meta_data'].id),
                            default=table_data['table_meta_data'].name)

<<<<<<< Updated upstream
            # logging.info('get_table ' + table_name + ' time: ' + str(time.time() - start_time))
=======
                if child_data:
                    row_counter = self.linked_data(child_tables, child_data, row_name, row_counter, depth,
                                                   list(row_names.keys()), (current_depth + 1))
>>>>>>> Stashed changes

        self.classattr['form_data_max_level_0'] = \
            HiddenField('form_data_max_level_0', default=level)

        # logging.info('row_counter: ' + str(row_counter))

    def row_fields(self, row_count, row_name, table_meta_data):
        table_id_field = HiddenField('record_data_table_id_'+str(row_count), default=table_meta_data.id)
        table_name_field = HiddenField('record_data_table_'+str(row_count), default=table_meta_data.name)
        row_field = HiddenField('record_data_row_name_'+str(row_count), default=row_name)

        return {'record_data_row_name_'+str(row_count): row_field,
                'record_data_table_'+str(row_count): table_name_field,
                'record_data_table_id_'+str(row_count): table_id_field}

<<<<<<< Updated upstream
    def get_row(self, data_instance, table_name, instance, control_type, row_counter):
        # start_time = time.time()
        # logging.info('row_name: ' + instance.name)
        self.classattr['start_row_'+str(row_counter)]=\
            HiddenField('start_row_'+str(row_counter))
=======
    def get_row(self, fields, row_name, row_counter, control_type, data):
        # logging.info('row_name: ' + row_name)
        data.get_data(row_name)
>>>>>>> Stashed changes

        for field_name, field in data_instance.fields[table_name].fields.items():
            # field_start = time.time()
            field_display_name = field.display_name.title()

            value = getattr(instance, field.Field.display_name)

            control_id = 'data_entry_' + field.Field.display_name+"_"+str(row_counter)
            # logging.info('control_id: ' + str(control_id))
            # logging.info('control_type: ' + str(control_type))
            # logging.info('value: ' + str(value))
            self.classattr[control_id] = self.input_field(field, field_display_name, getattr(instance, 'name'),
                                                          control_id, control_type, value)

            # logging.info('input_field ' + field_display_name + ' time: ' + str(time.time() - field_start))

<<<<<<< Updated upstream
        self.classattr['end_row_'+str(row_counter)]=\
            HiddenField('end_row_'+str(row_counter))

        # logging.info('get_row time: ' + str(time.time() - start_time))
=======
        return data.get_value('id')
>>>>>>> Stashed changes
