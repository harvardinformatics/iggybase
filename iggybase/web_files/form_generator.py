from types import new_class
from flask.ext.wtf import Form
from wtforms import HiddenField
from wtforms.validators import DataRequired, Length, email, Optional
from iggybase.core.data_instance import DataInstance
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
        self.table_meta_data = None
        self.dropdowns = {}
        self.form_class = None

    def page_template_context(self):
        return super(FormGenerator, self).page_template_context(table_name=self.table_name,
                                                                form=self.form_class,
                                                                form_type=self.form_type)

    def input_field(self, field_data, display_name, row_name, control_id, control_type, value=None):
        logging.info('row_name: ' + str(row_name) + '  display_name: ' + str(display_name))
        kwargs = {}
        validators = []
        if value is not None:
            logging.info('input_field value: ' + str(value))
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

                    if value is None:
                        self.classattr['id_' + control_id] = HiddenField('id_' + control_id)
                    else:
                        value = [item for item in choices if item[0] == value]

                        if len(value) > 0:
                            # logging.info(display_name + ' value[0][0]: ' + str(value[0][0]))
                            # logging.info(display_name + ' value[0][1]: ' + str(value[0][1]))
                            kwargs['default'] = value[0][1]

                            self.classattr['id_' + control_id] = HiddenField('id_' + control_id, default=value[0][0])
                        else:
                            self.classattr['id_' + control_id] = HiddenField('id_' + control_id)

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
            self.classattr['files_' + control_id] = HiddenField('files_' + control_id, default=value)
            return IggybaseFileField(display_name, **kwargs)
        elif field_data.Field.data_type_id == constants.TEXT_AREA:
            return IggybaseTextAreaField(display_name, **kwargs)
        else:
            return IggybaseStringField(display_name, **kwargs)

    def empty_form(self):
        self.form_class = new_class('EmptyForm', (Form,))

    def multiple_data_entry_form(self, row_names=[], data_instance = None):
        if data_instance is None:
            data_instance = DataInstance(self.table_name)
            data_instance.get_multiple_data(row_names)

        self.get_table(data_instance)

        self.classattr['form_data_table_0'] = HiddenField('form_data_table_0', default=self.table_name)
        self.classattr['form_data_type_0'] =  HiddenField('form_data_type_0', default=self.form_type)

        row_counter = 0
        for row_name in row_names:
            self.classattr['form_data_row_name_' + str(row_counter)] = \
                HiddenField('form_data_row_name_' + str(row_counter), default=row_name)
            row_counter += 1

        # logging.info('row_names')
        # logging.info(row_names)
        # logging.info('data_instance.instances[self.table_name]')
        # logging.info(data_instance.instances[self.table_name])

        self.classattr['row_counter'] = HiddenField('row_counter', default=data_instance.instance_counter)

        form_class = new_class('MultipleForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        self.form_class = form_class(None)

    def data_entry_form(self, row_name='new', data_instance = None, depth = 2):
        if data_instance is None:
            data_instance = DataInstance(self.table_name, row_name)

        if row_name != 'new':
            data_instance.get_linked_instances(depth)

        self.get_table(data_instance)

        self.classattr['form_data_type_0'] = HiddenField('form_data_type_0', default=self.form_type)
        self.classattr['form_data_table_0'] = HiddenField('form_data_table_0', default=self.table_name)
        self.classattr['form_data_row_name_0'] = HiddenField('form_data_row_name_0', default=row_name)
        self.classattr['row_counter'] = HiddenField('row_counter', default=data_instance.instance_counter)

        form_class = new_class('SingleForm', (Form,), {}, lambda ns: ns.update(self.classattr))

        self.form_class = form_class(None)

    def get_table(self, data_instance):
        row_counter = 0
        level = 0

        table_context = []

        for context in self.page_context:
            if context not in ['base-context', 'workflow','modal_form']:
                table_context.append(context)
            
        for table_name, table_data in data_instance.tables.items():
            # start_time = time.time()
            # logging.info('get_table loop table_name: ' + table_name)
            if table_name == 'history':
                continue

            if table_data['link_data'] is not None:
                link_field = self.role_access_control.has_access('Field',
                                                                 {'id': table_data['link_data'].child_link_field_id})

                self.classattr['linkcolumn_' + str(table_data['table_meta_data'].id)] = \
                    HiddenField('linkcolumn_' + str(table_data['table_meta_data'].id), default=link_field.display_name)

            self.classattr['table_level_' + str(table_data['table_meta_data'].id)] = \
                HiddenField('table_level_' + str(table_data['table_meta_data'].id), default=table_data['level'])

            if level < table_data['level']:
                level = table_data['level']

            self.classattr['table_name_' + str(table_data['table_meta_data'].id)] = \
                HiddenField('table_name_' + str(table_data['table_meta_data'].id),
                            default=table_data['table_meta_data'].name)

            if table_data['level'] == 0 and self.form_type == 'single':
                control_type = 'data-control'
                temp_page_context = ['main-table'] + table_context
                buttons = self.role_access_control.page_form_buttons(self.page_form_ids, temp_page_context,
                                                                     table_data['table_meta_data'].id)
            elif self.form_type == 'single':
                control_type = 'table-control'
                temp_page_context = ['child-table'] + table_context
                buttons = self.role_access_control.page_form_buttons(self.page_form_ids, temp_page_context,
                                                                    table_data['table_meta_data'].id)
            else:
                control_type = 'table-control'
                temp_page_context = ['multiple'] + table_context
                buttons = self.role_access_control.page_form_buttons(self.page_form_ids, temp_page_context,
                                                                     table_data['table_meta_data'].id)

            # logging.info('temp_page_context ' + table_name)
            # logging.info(temp_page_context)

            context = {'table_name': table_data['table_meta_data'].name,
                       'table_id': str(table_data['table_meta_data'].id),
                       'table_level': str(table_data['level']),
                       'table_title': table_data['table_meta_data'].name.replace("_", " ").title()}

            buttons['top'], buttons['bottom'] = self.button_html_generator(buttons, context)

            # logging.info('buttons[top] ' + table_name)
            # logging.info(buttons['top'])
            # logging.info('buttons[bottom] ' + table_name)
            # logging.info(buttons['bottom'])

            if buttons['top']:
                self.classattr[table_name + '_buttons_top'] =  HiddenField('buttons_top', default=buttons['top'])

            self.classattr['start_table_' + str(table_data['table_meta_data'].id)] = \
                HiddenField('start_table_' + str(table_data['table_meta_data'].id),
                            default=table_data['table_meta_data'].name)

            for instance_name, instance in data_instance.instances[table_name].items():
                # logging.info(instance_name + '  ' + table_data['table_meta_data'].name)

                self.classattr.update(self.row_fields(row_counter, instance_name, table_data['table_meta_data']))
                self.get_row(data_instance, table_name, instance, control_type, row_counter)

                row_counter += 1

            if buttons['bottom']:
                self.classattr[table_name + '_buttons_bottom'] =  HiddenField('buttons_bottom', default=buttons['bottom'])

            self.classattr['end_table_' + str(table_data['table_meta_data'].id)] = \
                HiddenField('end_table_' + str(table_data['table_meta_data'].id),
                            default=table_data['table_meta_data'].name)

            # logging.info('get_table ' + table_name + ' time: ' + str(time.time() - start_time))

        self.classattr['form_data_max_level_0'] = \
            HiddenField('form_data_max_level_0', default=level)

        # logging.info('row_counter: ' + str(row_counter))

    def row_fields(self, row_count, row_name, table_meta_data):
        table_id_field = HiddenField('record_data_table_id_'+str(row_count), default=table_meta_data.id)
        table_name_field = HiddenField('record_data_table_'+str(row_count), default=table_meta_data.name)
        row_field = HiddenField('record_data_row_name_'+str(row_count), default=row_name)
        if row_name == 'new':
            row_new = HiddenField('record_data_row_new_'+str(row_count), default=1)
        else:
            row_new = HiddenField('record_data_row_new_'+str(row_count), default=0)

        return {'record_data_row_name_'+str(row_count): row_field,
                'record_data_table_'+str(row_count): table_name_field,
                'record_data_new_'+str(row_count): row_new,
                'record_data_table_id_'+str(row_count): table_id_field}

    def button_html_generator(self, buttons, context):
        html_buttons = {'top': '', 'bottom': ''}
        page_context = " ".join(self.page_context).replace("base-context", "")

        for button_location, btns in buttons.items():
            for button in btns:
                html_buttons[button_location] += ('<input value="' + button.button_value +
                                                  '" id="' + button.button_id +
                                                  '" name="' + button.button_id +
                                                  '" type="' + button.button_type +
                                                  '" context="' + page_context +
                                                  '" class="' + button.button_class + " " + page_context + '"')

                if button.special_props:
                    html_buttons[button_location] += button.special_props

                html_buttons[button_location] += '>'

        html_buttons['top'] = html_buttons['top'].replace('<page_context>', page_context)
        html_buttons['bottom'] = html_buttons['bottom'].replace('<page_context>', page_context)

        if 'table_name' in context:
            html_buttons['top'] = html_buttons['top'].replace('<table_name>', context['table_name'])
            html_buttons['bottom'] = html_buttons['bottom'].replace('<table_name>', context['table_name'])

        if 'table_title' in context:
            html_buttons['top'] = html_buttons['top'].replace('<table_title>', context['table_title'])
            html_buttons['bottom'] = html_buttons['bottom'].replace('<table_title>', context['table_title'])

        if 'table_id' in context:
            html_buttons['top'] = html_buttons['top'].replace('<table_id>', context['table_id'])
            html_buttons['bottom'] = html_buttons['bottom'].replace('<table_id>', context['table_id'])

        if 'table_level' in context:
            html_buttons['top'] = html_buttons['top'].replace('<table_level>', context['table_level'])
            html_buttons['bottom'] = html_buttons['bottom'].replace('<table_level>', context['table_level'])

        if 'row_name' in context:
            html_buttons['top'] = html_buttons['top'].replace('<instance_name>', context['row_name'])
            html_buttons['bottom'] = html_buttons['bottom'].replace('<instance_name>', context['row_name'])

        return html_buttons['top'], html_buttons['bottom']

    def get_row(self, data_instance, table_name, instance, control_type, row_counter):
        # start_time = time.time()
        # logging.info('row_name: ' + str(instance['instance'].name))
        self.classattr['start_row_'+str(row_counter)]=\
            HiddenField('start_row_'+str(row_counter))

        for field_name, field in data_instance.fields[table_name].fields.items():
            # field_start = time.time()
            field_display_name = field.display_name.title()

            value = getattr(instance['instance'], field.Field.display_name)

            if field.Field.display_name == 'name' and value == 'new':
                value = None

            control_id = 'data_entry_' + field.Field.display_name + "_" + str(row_counter)
            # logging.info('control_id: ' + str(control_id))
            # logging.info('control_type: ' + str(control_type))
            # logging.info('value: ' + str(value))
            self.classattr[control_id] = self.input_field(field, field_display_name,
                                                          getattr(instance['instance'], 'name'),
                                                          control_id, control_type, value)

            # logging.info('input_field ' + field_display_name + ' time: ' + str(time.time() - field_start))

        self.classattr['end_row_'+str(row_counter)]=\
            HiddenField('end_row_'+str(row_counter))

        # logging.info('get_row time: ' + str(time.time() - start_time))
