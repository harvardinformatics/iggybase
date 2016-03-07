import iggybase.templating as templating
from flask import g, redirect, url_for

def index():
    return templating.render_template( 'index.html' )

def default():
    return templating.page_template('index.html')

def message(page_temp, page_msg):
    return templating.page_template(page_temp, page_msg=page_msg)

def forbidden():
    return templating.page_template('forbidden')

def page_not_found():
    return templating.page_template('not_authorized')

def home():
    """redirects to user home page
    """
    if not g.user:
        abort( 403 )
    if g.user.home_page:
        home_page = g.user.home_page
    else:
        # TODO: we need to dynamically come up with facility
        home_page = url_for('core.detail', facility_name = 'murray', table_name =
        'user', row_name = g.user.name)
    return redirect( home_page )
