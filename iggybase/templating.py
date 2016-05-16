from flask import render_template, abort, request, g
from iggybase import utilities as util
import logging

def page_template_context(page_form_name, **context):
    access_ctrl = util.get_role_access_control()

    context['page_form_name'] = page_form_name
    context['url_root'] = request.url_root

    # add button, nav bar, side bar
    page_form, buttons, scripts = access_ctrl.get_page_form_data(page_form_name, True)

    if page_form is None:
        abort(403)

    context['template'] = page_form.page_template
    context['page_header'] = page_form.page_header
    context['page_title'] = page_form.page_title

    context['top_buttons'] = buttons['top']
    submit_action_url = page_button_action(
        buttons['top']
    )

    context['bottom_buttons'] = buttons['bottom']
    submit_action_url = page_button_action(
        buttons['bottom']
    )

    submit_action_url = submit_action_url.replace('<facility>', g.facility)

    if 'btn_overrides' in context:
        if 'top' in context['btn_overrides']:
            buttons['top'] = btn_overrides(buttons['top'],
            context['btn_overrides']['top'])
        elif 'bottom' in context['btn_overrides']:
            buttons['bottom'] = btn_overrides(buttons['bottom'],
            context['btn_overrides']['bottom'])

    context['scripts'] = page_scripts(scripts)
    if not 'hidden_fields' in context:
        context['hidden_fields'] = {}
    context['hidden_fields'].update({
        'url_root': context['url_root']
    })
    context['hidden_fields'].update({
        'facility': g.facility
    })
    if 'module_name' in context:
        submit_action_url = submit_action_url.replace('<module>', context['module_name'])
        context['hidden_fields'].update({
            'mod': context['module_name']
        })

    if 'table_name' in context:
        submit_action_url = submit_action_url.replace('<table>', context['table_name'])
        context['hidden_fields'].update({
            'table': context['table_name']
        })
    ## Menus
    navbar, sidebar = access_ctrl.page_form_menus(page_form.id)
    context.update({'navbar': navbar, 'sidebar': sidebar})

    if submit_action_url == '' or "<" in submit_action_url:
        context['submit_action_url'] = ''
    else:
        context['submit_action_url'] = request.url_root + submit_action_url

    # logging.info( context )

    return context

def page_button_action(buttons):
    submit_action_url = ''

    for button in buttons:
        if button.submit_action_url is not None:
            submit_action_url = button.submit_action_url

    return submit_action_url

def page_scripts(scripts):
    scpts = []

    for script in scripts:
        scpts.append(script.page_javascript)

    return scpts

def btn_overrides(buttons, overrides):
    for btn in buttons:
        if btn.button_id in overrides:
            for key, val in overrides[btn.button_id].items():
                if hasattr(btn, key):
                    setattr(btn, key, val)

