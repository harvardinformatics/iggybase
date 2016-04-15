import iggybase.templating as templating
from flask import g, redirect, url_for, abort, redirect
from flask_security.core import current_user

def index():
    return templating.render_template( 'index.html' )

def default():
    return templating.page_template('index.html')

def message(page_temp, page_msg):
    return templating.page_template(page_temp, page_msg=page_msg)

def forbidden():
    if not current_user.is_authenticated:
        return redirect(url_for('security.login'))
    else:
        return templating.page_template('forbidden')

def page_not_found():
    if not current_user.is_authenticated:
        return redirect(url_for('security.login'))
    else:
        return templating.page_template('not_authorized')

def home():
    """redirects to user home page
    """
    if not current_user.is_authenticated:
        redirect(url_for('security.login'))
    if g.user.home_page:
        home_page = g.user.home_page
    else:
        # TODO: we need to dynamically come up with facility
        home_page = url_for('core.detail', facility_name = 'murray', table_name =
        'user', row_name = g.user.name)
    return redirect( home_page )
