from flask import g, request
from flask.ext.login import login_required, current_user
from iggybase.templating import page_template
from iggybase.mod_core import mod_core
from iggybase.database import db_session
from iggybase.mod_murray import models
from iggybase.form_generator import FormGenerator
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl

import logging

@mod_core.before_request
@login_required
def before_request():
    g.user = current_user

@mod_core.route( '/' )
def default():
    return page_template( 'index.html' )

@mod_core.route( '/lookup/<table_name>/<column_name>' )
def lookup( table_name, column_name ):
    fg = FormGenerator( 'mod_core', table_name )
    form = fg.lookup_form( column_name )
    organization_access_control = OrganizationAccessControl( 'mod_core' )
    results = organization_access_control.get_summary_data( table_name )
    table_rows = organization_access_control.format_data(results)
    return page_template( 'lookup', form = form, buttons_only = True, table_name = table_name,
                          column_name = column_name )


@mod_core.route( '/lookup_results' )
def lookup( table_name, column_name ):
    fg = FormGenerator( 'mod_core', table_name )
    form = fg.lookup_form( column_name )
    organization_access_control = OrganizationAccessControl( 'mod_core' )
    results = organization_access_control.get_summary_data( table_name )
    table_rows = organization_access_control.format_data(results)
    return page_template( 'lookup', form = form, buttons_only = True, table_name = table_name,
                          column_name = column_name )


@mod_core.route( '/summary/<table_name>' )
def summary( table_name = None ):
    organization_access_control = OrganizationAccessControl( 'mod_core' )
    results = organization_access_control.get_summary_data( table_name )
    table_rows = organization_access_control.format_data(results)
    return page_template( 'summary', table_name = table_name, table_rows =
            table_rows )

@mod_core.route( '/detail/<table_name>/<row_name>' )
def detail( table_name = None, row_name= None ):
    organization_access_control = OrganizationAccessControl( 'mod_core' )
    results = organization_access_control.get_summary_data( table_name, row_name )
    table_rows = organization_access_control.format_data(results)
    mod = request.path.split('/')[1]
    hidden_fields = {'mod': mod, 'table': table_name, 'row_name': row_name}
    return page_template( 'detail', table_name = table_name, row_name = row_name, table_rows = table_rows, hidden_fields = hidden_fields)

@mod_core.route( '/data_entry/<table_object>/<row_name>' )
def murray_lab_data_entry( table_object = None, row_name = None ):
    fg = FormGenerator( 'mod_core', table_object )
    form = fg.default_single_entry_form( row_name )

    if form.validate_on_submit( ):
        session = db_session( )
        table_object = getattr( models, form.table_object.data )

        pass

    return page_template( 'single_data_entry', form = form )
