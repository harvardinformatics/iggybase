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
    else:
        # add button, nav bar, side bar
        pass

    return render_template( page_form, **context )