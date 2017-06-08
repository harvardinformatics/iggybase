from types import new_class
from flask import request, g
from flask.ext.wtf import Form
from wtforms import HiddenField
import datetime
from wtforms.validators import DataRequired, Length, email, Optional
from iggybase.core.instance_collection import InstanceCollection
from iggybase.web_files.iggybase_form_objects import IggybaseFormTable
from iggybase.web_files import constants
from iggybase.web_files.page_template import PageTemplate
from iggybase.web_files.iggybase_form_fields import IggybaseBooleanField, IggybaseDateField, IggybaseFloatField,\
    IggybaseIntegerField, IggybaseLookUpField, IggybaseStringField, IggybaseTextAreaField, IggybaseSelectField,\
    IggybaseFileField, IggybasePasswordField, IggybaseDecimalField, IggybaseDateTimeField
import logging


class FormGenerator(PageTemplate):
    def __init__(self, page_form_name, form_type, table_name, page_context, module_name):
        super(FormGenerator, self).__init__(module_name, page_form_name, page_context)
        self.table_name = table_name
        self.form_type = form_type
        self.classattr = {}
        self.dropdowns = {}
        self.form_class = None
        self.form_tables = []
        self.context = {'table_name': self.table_name, 'form_type': self.form_type}
        self.instances = None

    def page_template_context(self):
        self.context['submit_action_url'] = self.get_submit_action_url()
        self.context['form'] = self.form_class
        self.context['form_tables'] = self.form_tables
        return super(FormGenerator, self).page_template_context(**self.context)

    def add_page_context(self, context=None):
        if context is not None:
            for k, v in context.items():
                self.context[k] = v

    def input_field(self, instance, field_name, display_name, control_id, field_class,
                    value=None):
        kwargs = {}
        validators = []

        if value is not None:
            kwargs['default'] = value

        # no validators or classes attached to hidden fields, as it could cause issues
        # e.g. an empty hidden required field
        if not instance.field_roles[field_name] or instance.field_roles[field_name].visible != constants.VISIBLE:
            return HiddenField(instance.columns[field_name].display_name, **kwargs)

        kwargs['instance_name'] = instance.instance_name
        kwargs['table_object'] = instance.table_name

        if instance.columns[field_name].description != "":
            kwargs['title'] = instance.columns[field_name].description

        if instance.field_roles[field_name].required == constants.REQUIRED:
            validators.append(DataRequired())
        else:
            validators.append(Optional())

        if instance.columns[field_name].length is not None and \
                        instance.columns[field_name].data_type_id == constants.STRING:
            validators.append(Length(0, instance.columns[field_name].length))

        if "email" in instance.columns[field_name].display_name:
            validators.append(email())

        kwargs['validators'] = validators
        kwargs['iggybase_class'] = field_class

        if ((instance.field_roles[field_name].permission_id == constants.DEFAULTED and \
                         instance.instance_name != 'new') or
                (instance.field_roles[field_name].permission_id == constants.IMMUTABLE and \
                             instance.instance_name == 'new') or
                (instance.field_roles[field_name].permission_id == constants.READ_WRITE)):
            kwargs['readonly'] = False
        else:
            kwargs['readonly'] = True

        if instance.columns[field_name].select_list_id is not None:
            choices = self.organization_access_control.get_select_list(instance.columns[field_name].select_list_id)

            if kwargs['readonly']:
                value = [item for item in choices if item[0] == value]

                if len(value) > 0:
                    kwargs['default'] = value[0][1]

                return IggybaseStringField(display_name, **kwargs)
            else:
                kwargs['coerce'] = int
                kwargs['choices'] = choices

                return IggybaseSelectField(display_name, **kwargs)
        elif instance.columns[field_name].foreign_key_field_id is not None:
            if instance.columns[field_name].name not in self.dropdowns:
                if field_name in instance.foreign_keys_display.keys():
                    # case of adding a foriegn key data to a field
                    self.dropdowns[instance.columns[field_name].name] = self.organization_access_control.\
                        get_foreign_key_data(instance.columns[field_name].fk_table_object,
                                             instance.foreign_keys_display[field_name])

            choices = self.dropdowns[instance.columns[field_name].name]

            if instance.columns[field_name].drop_down_list_limit:
                drop_down_limit = instance.columns[field_name].drop_down_list_limit
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
        elif instance.columns[field_name].data_type_id == constants.INTEGER:
            return IggybaseIntegerField(display_name, **kwargs)
        elif instance.columns[field_name].data_type_id == constants.FLOAT:
            return IggybaseFloatField(display_name, **kwargs)
        elif instance.columns[field_name].data_type_id == constants.DECIMAL:
            return IggybaseDecimalField(display_name, **kwargs)
        elif instance.columns[field_name].data_type_id == constants.BOOLEAN:
            self.classattr['bool_' + control_id]=HiddenField('bool_' + control_id, default=bool(value))
            return IggybaseBooleanField(display_name, **kwargs)
        elif instance.columns[field_name].data_type_id == constants.DATE:
            return IggybaseDateField(display_name, **kwargs)
        elif instance.columns[field_name].data_type_id == constants.DATETIME:
            return IggybaseDateTimeField(display_name, **kwargs)
        elif instance.columns[field_name].data_type_id == constants.PASSWORD:
            return IggybasePasswordField(display_name, **kwargs)
        elif instance.columns[field_name].data_type_id == constants.FILE:
            self.classattr['files_' + control_id] = HiddenField('files_' + control_id, default=value)
            return IggybaseFileField(display_name, **kwargs)
        elif instance.columns[field_name].data_type_id == constants.TEXT_AREA:
            return IggybaseTextAreaField(display_name, **kwargs)
        else:
            return IggybaseStringField(display_name, **kwargs)

    def data_entry_form(self, row_names=['new'], instances = None, depth = 2):
        self.form_class = None
        self.classattr = {}
        self.form_tables = []

        if instances is None:
            self.instances = InstanceCollection(depth, {self.table_name: row_names})

            if self.instances.instance.new_instance == False and self.form_type == 'SingleForm':
                self.instances.get_linked_instances(self.instances.instance.instance.id)
        else:
            self.instances = instances

        # for table_name in self.instances.table_instances.keys():
        #     for instance_name, instance_data in self.instances.table_instances[table_name].items():
        #         logging.info('instance_data.instance.name: ' + str(instance_data.instance.name))
        #         logging.info('instance_data.instance_name: ' + str(instance_data.instance_name))
        #         logging.info('instance_data.instance.table_name: ' + str(instance_data.table_name))

        row_index = self.get_table()

        self.classattr['row_counter'] = HiddenField('row_counter', default=row_index)
        self.classattr['max_depth'] = HiddenField('max_depth', default=depth)


        form_class = new_class(self.form_type, (Form,), {}, lambda ns: ns.update(self.classattr))

        self.form_class = form_class(None)
        
    def get_table(self):
        row_index = 0

        table_context = []

        for context in self.page_context:
            if context not in ['base-context', 'workflow','modal_form']:
                table_context.append(context)

        for table_name, table_data in self.instances.tables.items():
            if table_name == 'history' or not self.instances.table_instances[table_name]:
                continue

            table_id = table_data.table_object.id
            table_level = table_data.level

            if table_data.link_data is not None:
                link_field = self.role_access_control.has_access('Field',
                                                                 {'id': table_data.link_data.child_link_field_id})

                self.classattr['linkcolumn_' + str(table_id)] = HiddenField('linkcolumn_' + str(table_id),
                                                                            default=link_field.Field.display_name)

            self.classattr['table_name_' + str(table_id)] = HiddenField('table_name_' + str(table_id),
                                                                        default=table_name)

            title = table_data.table_display_name.replace('_', ' ').title()
            if (table_level == 0 and self.form_type == 'SingleForm') or 'modal_form' in self.page_context:
                form_table = IggybaseFormTable(table_name,
                                               title + ' ' + self.page_form.page_header.replace("_", " ").title(),
                                               table_level)
                control_type = 'data-control'
                temp_page_context = ['main-table'] + table_context
                buttons = self.role_access_control.page_form_buttons(self.page_form_ids, temp_page_context, table_id)
            elif self.form_type == 'SingleForm':
                form_table = IggybaseFormTable(table_name,
                                               title,
                                               table_level,
                                               'horizontal')
                control_type = 'table-control'
                temp_page_context = ['child-table'] + table_context
                buttons = self.role_access_control.page_form_buttons(self.page_form_ids, temp_page_context, table_id)
            else:
                form_table = IggybaseFormTable(table_name,
                                               title,
                                               table_level,
                                               'horizontal')
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

            if table_level == 0:
                self.classattr['main_table'] = HiddenField('main_table', default=table_name)
                self.classattr['base_instance'] = HiddenField('base_instance',
                                                              default=self.instances.base_instance.instance_name)
                top_buttons, bottom_buttons = self.button_generator(self.buttons, context)
                form_table.add_buttons(top_buttons, bottom_buttons)

            top_buttons, bottom_buttons = self.button_generator(buttons, context)
            form_table.add_buttons(top_buttons, bottom_buttons)

            instances = sorted(list(self.instances.table_instances[table_name].values()), key=lambda x: x.form_index)

            for instance in instances:
                self.get_row(form_table, instance, control_type)

                if row_index < int(instance.form_index):
                    row_index = int(instance.form_index)

            self.form_tables.append(form_table)

        return row_index

    def get_row(self, form_table, instance, control_type):
        # logging.info('instance.instance.name: ' + str(instance.instance.name))
        # logging.info('instance.form_index: ' + str(instance.form_index))
        # logging.info('instance.instance_name: ' + str(instance.instance_name))
        # logging.info('instance.instance.table_name: ' + str(instance.table_name))
        record_index = form_table.add_new_record(instance.instance.name)

        for field_name, field in instance.columns.items():
            if field.field_class is not None:
                field_class = control_type + ' ' + field.field_class
            else:
                field_class = control_type

            if instance.field_roles[field_name] and instance.field_roles[field_name].visible:
                form_table.field_display_names.append({'name': field.display_name.title(),
                                                       'required': instance.field_roles[field_name].required,
                                                       'wide': 'wide' in field_class})

            value = getattr(instance.instance, field_name)

            if field_name == 'name' and ('empty_row' in value or 'new' in value):
                form_table[record_index].new_record = True
                value = None

            if instance.new_instance:
                control_str = form_table.table_name + "-" + field_name + "-" + instance.instance.name
            else :
                control_str = form_table.table_name + "-" + field_name + "-" + str(instance.instance.id)

            control_id = 'data_entry-' + control_str + "-" + str(instance.form_index)

            self.classattr[control_id] = self.input_field(instance, field_name,
                                                          instance.field_display_name(field_name).title(),
                                                          control_id, field_class, value)

            form_table[record_index].add_new_field(control_id, field_class)

    def get_submit_action_url(self):
        url = ''

        for button_locations, button_objects in self.buttons.items():
            for button in button_objects:
                if button.submit_action_url is not None:
                    url = button.submit_action_url

        if url != '':
            url = url.replace('<facility>', g.facility)
            url = url.replace('<module>', self.module_name)
            url = url.replace('<table>', self.table_name)

        if url == '' or "<" in url:
            return ''
        else:
            return request.url_root + url
