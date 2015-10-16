from flask.ext.login import login_required
from iggybase.templating import render_template
from iggybase.mod_core import mod_core
import logging

@mod_core.before_request
@login_required
def before_request():
    pass

@mod_core.route( '/' )
def default():
    return render_template( 'index.html' )


@mod_core.route( '/summary/<page_type>' )
def summary( page_type = None ):
    logging.info( page_type + ' summary page user' )
    return render_template( 'mod_core/summary.html', form_type = 'summary', page_type = page_type )