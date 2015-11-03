from flask import render_template
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
from iggybase.mod_auth.facility_access_control import FacilityAccessControl
import logging

def page_template( page_form, **context ):
    access_ctrl = FacilityRoleAccessControl( )

    #logging.info( page_form )

    if access_ctrl.user is None:
        # add buttons only (login and related pages - no user)
        facility_access_ctrl = FacilityAccessControl( )

        buttons = facility_access_ctrl.facility_buttons( page_form )

        context[ 'buttons' ] = page_buttons( buttons )
    else:
        # add button, nav bar, side bar
        buttons = access_ctrl.facility_buttons( page_form )

        context[ 'buttons' ] = page_buttons( buttons )

    return render_template( page_form, **context )

def page_buttons( buttons ):
    btns = [ ]

    for button in buttons:
        btn_str = '<input value="' + button.button_value + '" id="' + button.button_id + \
                                '" name="' + button.button_id + '" type="' + button.button_type + \
                                '" class="' + button.button_class + '" '

        if button.special_props is not None:
            btn_str += button.special_props + '>'
        else:
            btn_str += '>'

        btns.append( btn_str )

    return btns
