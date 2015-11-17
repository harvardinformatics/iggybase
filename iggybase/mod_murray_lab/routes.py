from flask.ext.login import login_required
from iggybase.templating import page_template
from iggybase.mod_murray_lab import mod_lab
import logging

@mod_lab.before_request
@login_required
def before_request():
    pass

@mod_lab.route( '/' )
def default():
    return page_template( 'index.html' )


@mod_lab.route( '/summary/<table_object>' )
def summary( table_object = None ):
    return page_template( 'mod_murray_lab/summary', table_object = table_object )