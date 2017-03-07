from types import new_class
from flask.ext.wtf import Form
from wtforms import HiddenField
from wtforms.validators import DataRequired, Length, email, Optional
from iggybase import utilities as util
from iggybase.core.instance_collection import InstanceCollection
from iggybase.web_files import constants
from iggybase.web_files.page_template import PageTemplate
from iggybase.web_files.iggybase_form_fields import IggybaseBooleanField, IggybaseDateField, IggybaseFloatField,\
    IggybaseIntegerField, IggybaseLookUpField, IggybaseStringField, IggybaseTextAreaField, IggybaseSelectField,\
    IggybaseFileField, IggybasePasswordField
import logging


class FormGenerator(PageTemplate):
    def __init__(self, page_form_name, form_type, table_name, page_context, module_name):
        super(FormGenerator, self).__init__(module_name, page_form_name, page_context)
        self.table_name = table_name
        self.form_type = form_type
        self.classattr = {}
        self.dropdowns = {}
        self.form_class = None
        self.context = {'table_name': self.table_name, 'form_type': self.form_type}
        self.instance = None

    def page_template_context(self):
        self.context['form'] = self.form_class
        self.context['fg'] = self
        return super(FormGenerator, self).page_template_context(**self.context)

    def add_page_context(self, context = {}):
        for k, v in context.items():
            self.context[k] = v

    def input_field(self, field_data, display_name, table_name, row_name, control_id, control_type, control_str,
                    value=None):
        kwargs = {}
        validators = []

        if value is not None:
            kwargs['default'] = value

        # no validators or classes attached to hidden fields, as it could cause issues
        # e.g. an empty hidden required field
        if field_data.FieldRole.visible != constants.VISIBLE:
            return HiddenField(field_data.FieldRole.display_name, **kwargs)

        kwargs['instance_name'] = row_name
        kwargs['table_object'] = table_name

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

            if kwargs['readonly']:
                value = [item for item in choices if item[0] == value]

                if len(value) > 0:
                    kwargs['default'] = value[0][1]

                return IggybaseStringField(display_name, **kwargs)
            else:
                kwargs['coerce'] = int
                kwargs['choices'] = choices

                return IggybaseSelectField(display_name, **kwargs)
        elif field_data.is_foreign_key:
            if field_data.name not in self.dropdowns:
                self.dropdowns[field_data.name] = self.organization_access_control.\
                    get_foreign_key_data(field_data.FK_TableObject, field_data.FK_Field)

            choices = self.dropdowns[field_data.name]

            if field_data.Field.drop_down_list_limit:
                drop_down_limit = field_data.Field.drop_down_list_limit
            else:
                drop_down_limit = 25

            if len(choices) > drop_down_limit:
                if value is None:
                    self.classattr['id_' + control_id] = HiddenField('id_' + control_id)
                else:
                    value = [item for item in choices if item[0] == value]

                    if len(value) > 0:
                        kwargs['default'] = value[0][1]

                        self.classattr['id_' + control_id] = HiddenField('id_' + control_id, default=value[0][0])
                    else:
                        self.classattr['id_' + control_id] = HiddenField('id_' + control_id)

                return IggybaseLookUpField(display_name, **kwargs)
            elif kwargs['readonly']:
                value = [item for item in choices if item[0] == value]

                if value is None or len(value) > 0:
                    kwargs['default'] = value[0][1]

                if value is not None:
                    kwargs['default'] = value

                return IggybaseStringField(display_name, **kwargs)
            else:
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
            self.classattr['files_' + control_id] = HiddenField('files_' + control_id, default=value)
            return IggybaseFileField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.TEXT_AREA:
            return IggybaseTextAreaField(display_name, **kwargs)
        else:
            return IggybaseStringField(display_name, **kwargs)

    def data_entry_form(self, row_names=['new'], instances = None, depth = 2):
        self.form_class = None
        self.classattr = {}

        if instances is None:
            instances = InstanceCollection(depth, {self.table_name: row_names})

            if not instances[row_names[0]].new_instance and self.form_type == 'SingleForm':
                instances.get_linked_instances(instances[row_names[0]].instance.id)

        self.instance = instances

        self.get_table(instances)

        self.classattr['row_counter'] = HiddenField('row_counter', default=len(instances.instances))

        form_class = new_class(self.form_type, (Form,), {}, lambda ns: ns.update(self.classattr))

        self.form_class = form_class(None)

    def get_table(self, instances):
        row_counter = 0
        level = 0

        table_context = []

        for context in self.page_context:
            if context not in ['base-context', 'workflow','modal_form']:
                table_context.append(context)

        for table_name, table_data in instances.tables.items():
            if table_name == 'history' or table_name == 'long_text':
                continue

            table_id = table_data.table_object.id
            table_level = table_data.level

            if table_data.link_data is not None:
                link_field = self.role_access_control.has_access('Field',
                                                                 {'id': table_data.link_data.child_link_field_id})

                self.classattr['linkcolumn_' + str(table_id)] = HiddenField('linkcolumn_' + str(table_id),
                                                                            default=link_field.Field.display_name)

            self.classattr['table_level_' + str(table_id)] = HiddenField('table_level_' + str(table_id),
                                                                         default=table_level)

            if level < table_level:
                level = table_level

            self.classattr['table_name_' + str(table_id)] = HiddenField('table_name_' + str(table_id),
                                                                        default=table_name)

            if table_level == 0 and self.form_type == 'SingleForm':
                control_type = 'data-control'
                temp_page_context = ['main-table'] + table_context
                buttons = self.role_access_control.page_form_buttons(self.page_form_ids, temp_page_context, table_id)
            elif self.form_type == 'SingleForm':
                control_type = 'table-control'
                temp_page_context = ['child-table'] + table_context
                buttons = self.role_access_control.page_form_buttons(self.page_form_ids, temp_page_context, table_id)
            else:
                control_type = 'table-control'
                temp_page_context = ['multiple'] + table_context
                buttons = self.role_access_control.page_form_buttons(self.page_form_ids, temp_page_context, table_id)

            # TODO: fg is using the instance here, an example of the classes
            # tightly coupled.  Maybe instead we could have fg keep all the
            # table level info and use data_instance only for row values,
            # another alternative place for table level info is table query
            # we would just need to have the ability to get all tables by depth
            context = {'table_name': table_name,
                       'table_id': str(table_id),
                       'table_level': str(table_level),
                       'table_title': table_data.table_display_name.replace('_', ' ').title()}

            buttons['top'], buttons['bottom'] = self.button_generator(buttons, context)

            if buttons['top']:
                self.classattr[table_name + '_buttons_top'] =  HiddenField('buttons_top', default=util.html_buttons(buttons['top']))

            self.classattr['start_table_' + str(table_id)] = HiddenField('start_table_' + str(table_id),
                                                                         default=table_name)

            for instance_name, instance in instances.table_instances[table_name].items():
                self.get_row(instances, table_name, instance, control_type, row_counter)

                row_counter += 1

            if buttons['bottom']:
                self.classattr[table_name + '_buttons_bottom'] =  HiddenField('buttons_bottom',
                                                                              default=util.html_buttons(buttons['bottom']))

            self.classattr['end_table_' + str(table_id)] = HiddenField('end_table_' + str(table_id),default=table_name)

        self.classattr['max_level'] = HiddenField('max_level', default=level)

    def get_row(self, instances, table_name, instance, control_type, row_counter):
        self.classattr['start_row_'+str(row_counter)] = HiddenField('start_row_'+str(row_counter),
                                                                    default=instance.instance.name)

        for field_name, field in instances.tables[table_name].fields.items():
            field_display_name = field.display_name.title()

            value = getattr(instance.instance, field.Field.display_name)

            if field.Field.display_name == 'name' and value is not None and 'empty_row' in value:
                value = None

            if instance.new_instance:
                control_str = table_name + "-" + field.Field.display_name + "-" + instance.instance.name
            else :
                control_str = table_name + "-" + field.Field.display_name + "-" + str(instance.instance.id)

            control_id = 'data_entry-' + control_str
            self.classattr[control_id] = self.input_field(field, field_display_name,
                                                          table_name, instance.instance.name,
                                                          control_id, control_type, control_str, value)

        self.classattr['end_row_'+str(row_counter)] = HiddenField('end_row_'+str(row_counter))
