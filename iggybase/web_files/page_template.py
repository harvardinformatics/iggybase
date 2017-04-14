from flask import render_template, abort, request, g, Markup
from iggybase import g_helper
from iggybase.admin import constants as admin_consts
from collections import OrderedDict as OrderedDict
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

        # TODO: if change_user feature is used this will not reflect that change
        context['user'] = g.user.name
        context['module_name'] = self.module_name
        context['template'] = self.page_form.page_template
        context['page_header'] = self.page_form.page_header
        context['page_title'] = self.page_form.page_title
        context['top_buttons'], context['bottom_buttons'] = self.button_generator(self.buttons, context)

        # logging.info('context[top_buttons]: ' + context['top_buttons'])
        # logging.info('context[bottom_buttons]: ' + context['bottom_buttons'])

        context['scripts'] = self.page_scripts(self.scripts)

        if not 'hidden_fields' in context:
            context['hidden_fields'] = {}

        context['hidden_fields'].update({'url_root': context['url_root']})
        context['hidden_fields'].update({'facility': g.facility})

        if 'module_name' in context:
            context['hidden_fields'].update({'mod': context['module_name']})

        if 'table_name' in context:
            context['hidden_fields'].update({'table': context['table_name']})

        ## Menus
        # add home to navbar
        navbar = OrderedDict({'home': {
                'title': 'home',
                'url': '/home'
                }
        })
        navbar_root = self.role_access_control.get_menu(admin_consts.MENU_NAVBAR_ROOT)
        navbar.update(self.populate_menu(navbar_root.id, context))
        # add facility role change options to navbar
        navbar['Role'] = self.role_access_control.make_role_menu()
        # TODO: remove change user as it is, reconsider once we
        # remove user org_ids
        '''change_user = self.role_access_control.make_user_menu()
        if change_user:
            navbar['User'] = change_user
        '''
        sidebar_root = self.role_access_control.get_menu(admin_consts.MENU_SIDEBAR_ROOT)
        sidebar = self.populate_menu(sidebar_root.id, context)
        context.update({'navbar': navbar, 'sidebar': sidebar})

        return context

    def populate_menu(self, parent_id, context, active=1):
        menu = OrderedDict()
        items = self.role_access_control.get_menu_items(parent_id, active)
        for item in items:
            url = ''
            if item.Route and item.Route.url_path and item.Route.url_path != '':
                if g.facility != '':
                    url = g.facility + '/' + item.Module.name + '/' + item.Route.url_path
                else:
                    url = item.Module.name + '/' + item.Route.url_path
                if url and item.Menu.dynamic_suffix:
                    url += '/' + item.Menu.dynamic_suffix

                if url and item.Menu.url_params:
                    url += item.Menu.url_params

                if url:
                    url = request.url_root + url
                else:
                    url = '#'
                # add context to url, exp replace <user> with g.user.name
                url = self.add_context(url, context)

            menu[item.Menu.name] = {
                    'url': url,
                    'title': item.Menu.display_name,
                    'class': None,
                    'subs': self.populate_menu(item.Menu.id, context, active)
            }
        return menu

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
