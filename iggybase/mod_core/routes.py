from flask import g, request
from flask.ext.login import login_required, current_user
from iggybase.templating import page_template
from iggybase.mod_core import mod_core
from iggybase.database import db_session
from iggybase.mod_core import models
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
import logging

@mod_core.before_request
@login_required
def before_request():
    g.user = current_user

@mod_core.route( '/' )
def default():
    return page_template( 'index.html' )

@mod_core.route( '/summary/<table_name>' )
def summary( table_name = None ):
    organization_access_control = OrganizationAccessControl( 'mod_core' )
    results = organization_access_control.get_summary_data( table_name )
    table_rows = organization_access_control.format_data(results)
    return page_template( 'summary', table_name = table_name, table_rows =
            table_rows )
