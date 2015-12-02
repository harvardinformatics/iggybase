from flask import g, request
from flask.ext.login import login_required, current_user
from flask.ext import excel
from iggybase.templating import page_template
from iggybase.mod_murray import mod_murray
from iggybase.database import db_session
from iggybase.mod_murray import models
from iggybase.form_generator import FormGenerator
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl

import logging

@mod_murray.before_request
@login_required
def before_request():
    g.user = current_user

@mod_murray.route( '/' )
def default():
    return page_template( 'index.html' )


@mod_murray.route( '/summary/<table_name>' )
def summary( table_name = None ):
    organization_access_control = OrganizationAccessControl( 'mod_murray' )
    results = organization_access_control.get_summary_data( table_name )
    table_rows = organization_access_control.format_data(results)
    return page_template( 'summary', table_name = table_name, table_rows =
            table_rows )

@mod_murray.route( '/summary/<table_name>/download' )
def summary_download( table_name = None ):
    # TODO: consider reducing repeated code between summary and summary_download
    organization_access_control = OrganizationAccessControl( 'mod_murray' )
    results = organization_access_control.get_summary_data( table_name )
    table_rows = organization_access_control.format_download_data(results)
    csv = excel.make_response_from_array(table_rows, 'csv')
    return csv

@mod_murray.route( '/detail/<table_name>/<row_name>' )
def detail( table_name = None, row_name= None ):
    organization_access_control = OrganizationAccessControl( 'mod_murray' )
    results = organization_access_control.get_summary_data( table_name, row_name )
    table_rows = organization_access_control.format_data(results)
    mod = request.path.split('/')[1]
    hidden_fields = {'mod': mod, 'table': table_name, 'row_name': row_name}
    return page_template( 'detail', table_name = table_name, row_name = row_name, table_rows = table_rows, hidden_fields = hidden_fields)

@mod_murray.route( '/data_entry/<table_object>/<row_name>' )
def murray_lab_data_entry( table_object = None, row_name = None ):
    fg = FormGenerator( 'mod_murray', table_object )
    form = fg.default_single_entry_form( row_name )

    if form.validate_on_submit( ):
        organization_access_control = OrganizationAccessControl( 'mod_murray' )
        organization_access_control.save_form( form )

    return page_template( 'single_data_entry', form = form )
