from flask import render_template, abort, request, g
from iggybase.auth.role_access_control import RoleAccessControl
import logging

def page_template( page_form_name, **context ):
    access_ctrl = RoleAccessControl( )

    context['page_form_name'] = page_form_name
    context[ 'url_root' ] = request.url_root

    # add button, nav bar, side bar
    page_form = access_ctrl.has_access( "PageForm", {'name': page_form_name} )

    if page_form is None:
        abort( 403 )

    context[ 'page_header' ] = page_form.page_header
    context[ 'page_title' ] = page_form.page_title

    buttons = access_ctrl.page_form_buttons( page_form.id )

    context[ 'top_buttons' ] = page_buttons(
            buttons[ 'top' ]
    )
    context[ 'bottom_buttons' ] = page_buttons(
            buttons[ 'bottom' ]
    )

    scripts = access_ctrl.page_form_javascript( page_form.id )
    context[ 'scripts' ] = page_scripts( scripts )
    if not 'hidden_fields' in context:
        context['hidden_fields'] = {}
    context['hidden_fields'].update({
        'url_root': context['url_root']
    })
    context['hidden_fields'].update({
        'facility': g.facility
    })
    if 'module_name' in context:
        context['hidden_fields'].update({
            'mod': context['module_name']
        })

    if 'table_name' in context:
        context['hidden_fields'].update({
            'table': context['table_name']
        })
    ## Menus
    navbar, sidebar = access_ctrl.page_form_menus( page_form.id )
    context.update({'navbar': navbar, 'sidebar': sidebar})

    # logging.info( context )

    return render_template( page_form.page_template, **context )

def page_buttons( buttons ):
    btns = [ ]
    for button in buttons:
        btn_str = ' value="' + button.button_value + '" id="' + button.button_id + \
            '" name="' + button.button_id + '" type="' + button.button_type + \
            '" class="' + button.button_class  + '"'

        if button.special_props is not None:
            btn_str += button.special_props

        btns.append( btn_str )

    return btns

def page_scripts( scripts ):
    scpts = [ ]

    for script in scripts:
        scpts.append( script.page_javascript )

    return scpts
