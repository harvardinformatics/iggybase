from flask.ext.login import login_required, current_user
from iggybase.templating import page_template
from iggybase.mod_murray_lab import mod_murray_lab
from iggybase.form_generator import FormGenerator
from flask import g
import logging

@mod_murray_lab.before_request
@login_required
def before_request():
    g.user = current_user

@mod_murray_lab.route( '/' )
def default():
    return page_template( 'index.html' )


@mod_murray_lab.route( '/list/<table_object>' )
def summary( table_object = None ):
    return page_template( 'mod_murray_lab/summary', table_object = table_object )


@mod_murray_lab.route( '/data_entry/<table_object>/<row_name>' )
def data_entry( table_object = None, row_name = None ):
    fg = FormGenerator( 'mod_murray_lab', table_object )
    entry_form = fg.default_single_entry_form( row_name )
    return page_template( 'single_data_entry', form = entry_form )