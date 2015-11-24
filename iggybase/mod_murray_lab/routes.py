from flask import g
from flask.ext.login import login_required, current_user
from iggybase.templating import page_template
from iggybase.mod_murray_lab import mod_murray_lab
from iggybase.database import db_session
from iggybase.mod_murray_lab import models
from iggybase.form_generator import FormGenerator
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl

import logging

@mod_murray_lab.before_request
@login_required
def before_request():
    g.user = current_user

@mod_murray_lab.route( '/' )
def default():
    return page_template( 'index.html' )


@mod_murray_lab.route( '/summary/<table_name>' )
def summary( table_name = None ):
    organization_access_control = OrganizationAccessControl( 'mod_murray_lab' )
    table_rows = organization_access_control.get_summary_data( table_name )
    return page_template( 'summary', table_name = table_name, table_rows =
            table_rows )

@mod_murray_lab.route( '/detail/<table_name>/<row_name>' )
def detail( table_name = None, row_name= None ):
    organization_access_control = OrganizationAccessControl( 'mod_murray_lab' )
    table_rows = organization_access_control.get_summary_data( table_name, row_name )
    return page_template( 'detail', table_name = table_name, row_name = row_name, table_rows = table_rows)

@mod_murray_lab.route( '/data_entry/<table_object>/<row_name>' )
def murray_lab_data_entry( table_object = None, row_name = None ):
    fg = FormGenerator( 'mod_murray_lab', table_object )
    form = fg.default_single_entry_form( row_name )

    if form.validate_on_submit( ):
        session = db_session( )
        table_object = getattr( models, form.table_object.data )

        pass

    return page_template( 'single_data_entry', form = form )
