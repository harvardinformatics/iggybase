from flask.ext.login import login_required
from iggybase.templating import page_template
from iggybase.mod_core import mod_core
import logging

@mod_core.before_request
@login_required
def before_request():
    pass

@mod_core.route( '/' )
def default():
    return page_template( 'index.html' )


@mod_core.route( '/summary/<page_type>' )
def summary( page_type = None ):
    return page_template( 'mod_core/summary', page_type = page_type )