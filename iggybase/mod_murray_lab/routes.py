from flask import g
from flask.ext.login import login_required, current_user
from iggybase.templating import page_template
from iggybase.mod_murray_lab import mod_murray_lab
from iggybase.form_generator import FormGenerator
from iggybase.database import db_session
from iggybase.mod_auth import models

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
    table_rows = [u.__dict__ for u in db_session.query(getattr(models, table_name)).all()]
    return page_template( 'summary', table_name = table_name, table_rows =
            table_rows )


@mod_murray_lab.route( '/data_entry/<table_object>/<row_name>' )
def data_entry( table_object = None, row_name = None ):
    fg = FormGenerator( 'mod_murray_lab', table_object )
    form = fg.default_single_entry_form( row_name )

    if form.validate_on_submit( ):
        pass

    return page_template( 'single_data_entry', form = form )
