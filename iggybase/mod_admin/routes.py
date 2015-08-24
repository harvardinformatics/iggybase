from flask import redirect, url_for, request, session
from iggybase.templating import render_template
from . import mod_admin

@mod_admin.before_request
def check_valid_login():
    login_valid = 'user' in session

    if not login_valid:
        return redirect( url_for( 'mod_auth.login' ) )


@mod_admin.route( '/admin/console', methods = [ 'GET', 'POST' ] )
def console():
    return None
