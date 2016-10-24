from flask import render_template, abort, request, g, Markup
from iggybase import g_helper
import logging
import re

class PageTemplate():
    def __init__(self, module_name, page_form_name, page_context=None):
        # logging.info('page_form_name: ' + page_form_name)
        # logging.info('module_name: ' + module_name)
        # logging.info('page_context')
        # logging.info(page_context)

        if page_context is None:
            self.page_context = ['base-context']
        else:
            self.page_context = page_context.split(',')
            self.page_context.append('base-context')

        self.module_name = module_name
        self.page_form_name = page_form_name
        self.organization_access_control = g_helper.get_org_access_control()
        self.role_access_control = g_helper.get_role_access_control()

        self.page_form, self.page_form_ids = self.role_access_control.get_page_form_data(page_form_name,
                                                                                         self.page_context, True)

        if self.page_form is None:
            abort(403)

        self.buttons = self.role_access_control.page_form_buttons(self.page_form_ids, self.page_context)
        self.scripts = self.role_access_control.page_form_javascript(self.page_form_ids)

    def page_template_context(self, **context):
        context['page_form_name'] = self.page_form_name
        context['url_root'] = request.url_root

        context['page_context'] = " ".join(self.page_context)

        context['module_name'] = self.module_name
        context['template'] = self.page_form.page_template
        context['page_header'] = self.page_form.page_header
        context['page_title'] = self.page_form.page_title
        context['top_buttons'], context['bottom_buttons'] = self.button_generator(self.buttons, context)
        print(context['top_buttons'])
        print(context['bottom_buttons'])

        # logging.info('context[top_buttons]: ' + context['top_buttons'])
        # logging.info('context[bottom_buttons]: ' + context['bottom_buttons'])

        context['scripts'] = self.page_scripts(self.scripts)
        submit_action_url = self.page_button_action(self.buttons)

        if not 'hidden_fields' in context:
            context['hidden_fields'] = {}

        context['hidden_fields'].update({'url_root': context['url_root']})
        context['hidden_fields'].update({'facility': g.facility})

        if 'module_name' in context:
            if submit_action_url is not None:
                submit_action_url = submit_action_url.replace('<module>', context['module_name'])
            context['hidden_fields'].update({'mod': context['module_name']})

        if 'table_name' in context:
            context['hidden_fields'].update({'table': context['table_name']})
            if submit_action_url is not None:
                submit_action_url = submit_action_url.replace('<table>', context['table_name'])

        if submit_action_url is None or "<" in submit_action_url:
            context['submit_action_url'] = ''
        else:
            context['submit_action_url'] = request.url_root + submit_action_url

        ## Menus
        navbar, sidebar = self.role_access_control.page_form_menus()
        context.update({'navbar': navbar, 'sidebar': sidebar})

        return context

    def page_scripts(self, scripts):
        scpts = []

        for script in scripts:
            scpts.append(script.page_javascript)

        return scpts

    def add_context(self, val, context):
        # replace any <placeholder context> with the value from context
        if val:
            groups = re.findall('<(.*?)>', val)
            for g in groups:
                if g in context:
                    val = val.replace('<' + g + '>', context[g])
            return val
        else:
            return ''

    def button_generator(self, buttons, context):
        button_dict = {'top': [], 'bottom': []}
        page_context = " ".join(self.page_context).replace("base-context", "")

        for button_location, btns in buttons.items():
            for button in btns:
                button_dict[button_location].append({
                            'value': self.add_context(button.button_value, context),
                            'id': self.add_context(button.button_id, context),
                            'name': self.add_context(button.button_id, context),
                            'type': self.add_context(button.button_type, context),
                            'context': page_context,
                            'class': self.add_context(button.button_class + " " + page_context, context),
                            'special_props': self.add_context(button.special_props, context)
                        })

        return button_dict['top'], button_dict['bottom']

    def page_button_action(self, buttons):
        submit_action_url = None

        for button_locations, button_objects in buttons.items():
            for button in button_objects:
                if button.submit_action_url is not None:
                    submit_action_url = button.submit_action_url

        if submit_action_url is not None:
            submit_action_url = submit_action_url.replace('<facility>', g.facility)

        return submit_action_url
