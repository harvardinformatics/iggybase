from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required, login_user, logout_user
from .models import User
from . import mod_auth
from .forms import LoginForm

@mod_auth.route( '/login', methods = [ 'GET', 'POST' ] )
def login():
    form = LoginForm( )
    if form.validate_on_submit( ):
        user = User.query.filter_by( username=form.username.data ).first( )
        if user is None or not user.verify_password( form.password.data ):
            return redirect( url_for( 'main.login', **request.args ) )
        login_user( user, form.remember_me.data )
        return redirect( request.args.get( 'next' ) or url_for( 'main.index' ) )
    return render_template( 'mod_auth/login.html', form=form )


@mod_auth.route( '/logout' )
@login_required
def logout():
    logout_user()
    return redirect( url_for( 'main.index' ) )


@mod_auth.route( '/' )
def index( ):
    return render_template( 'index.html' )

