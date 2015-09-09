from flask import redirect, url_for, request, session
from iggybase.templating import render_template
from . import mod_core
from .forms import DefaultForm


@mod_core.before_request
def check_valid_login():
    login_valid = 'user' in session

    if not login_valid:
        return redirect( url_for( 'mod_auth.login' ) )


@mod_core.route( '/default' )
def default():
    form = DefaultForm( )
    return render_template( 'mod_core/default.html', form=form )