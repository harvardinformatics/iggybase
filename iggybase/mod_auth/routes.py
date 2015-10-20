from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required, login_user, logout_user, current_user
from iggybase.mod_auth.models import User
from iggybase.mod_admin.models import NewUser
from . import mod_auth
from iggybase.mod_auth.forms import LoginForm, RegisterForm
from iggybase.database import admin_db_session
import os
import socket
import logging

@mod_auth.route( '/login', methods = [ 'GET', 'POST' ] )
def login():
    form = LoginForm( )
    if form.validate_on_submit( ):
        user = User.query.filter_by( name=form.name.data ).first( )
        if user is None or not user.is_active( ) or not user.verify_password( form.password.data ):
            return render_template( 'mod_auth/failedlogin.html', form=form )
        login_user( user, form.remember_me.data )

        if user.home_page is not None:
            return redirect( request.args.get( 'next' ) or url_for( user.home_page, page_type = user.home_page_variable ) )
        else:
            return redirect( request.args.get( 'next' ) or url_for( 'mod_auth.index' ) )
    temp = render_template( 'mod_auth/login.html', form=form )
    index = temp.find( '</form>' )
    loginform = temp[ :index ] + '<input type="button" class="btn btn-default" id="login_register" value="Register" >' + temp[ index: ]
    return loginform


@mod_auth.route( '/register', methods = [ 'GET', 'POST' ] )
def register():
    form = RegisterForm( )
    if ( form.validate_on_submit( ) and form.password.data == form.confpassword.data ):
        rootdir = os.path.basename( os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) ) )
        hostname = socket.gethostname()

        session = admin_db_session( )

        newuser = NewUser( )

        newuser.address1 = form.address1.data
        newuser.address2 = form.address2.data
        newuser.active = False
        newuser.city = form.city.data
        newuser.email = form.email.data
        newuser.first_name = form.first_name.data
        newuser.group = form.group.data
        newuser.institution = form.institution.data
        newuser.last_name = form.last_name.data
        newuser.name = form.name.data
        newuser.phone = form.phone.data
        newuser.pi = form.pi.data
        newuser.postcode = form.zip.data
        newuser.state = form.state.data
        newuser.password_hash = User.get_password_hash( form.password.data )
        newuser.server = hostname
        newuser.directory = rootdir

        session.add( newuser )

        session.commit( )

        return redirect( url_for( 'mod_auth.regcomplete' ) )

    return render_template( 'mod_auth/register.html', form=form )


@mod_auth.route( '/logout' )
def logout():
    logout_user()
    return redirect( url_for( 'mod_auth.login' ) )


@mod_auth.route( '/' )
def index( ):
    return render_template( 'index.html' )


@mod_auth.route( '/regcomplete' )
def regcomplete( ):
    return render_template( 'mod_auth/regcomplete.html' )


@mod_auth.route( '/registererror' )
def registererror( ):
    return render_template( 'mod_auth/registererror.html' )


@mod_auth.route( '/failedlogin' )
def failedlogin( ):
    return render_template( 'mod_auth/failedlogin.html' )