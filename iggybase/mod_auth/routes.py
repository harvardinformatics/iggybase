from flask import render_template, redirect, url_for, request, flash
from flask.ext.login import login_required, login_user, logout_user
from .models import User
from . import mod_auth
from ..mod_core.models import Address
from .forms import LoginForm, RegisterForm
from iggybase.database import db_session
import logging

@mod_auth.route( '/login', methods = [ 'GET', 'POST' ] )
def login():
    form = LoginForm( )
    if form.validate_on_submit( ):
        user = User.query.filter_by( login_name=form.login_name.data ).first( )
        if user is None or not user.get_active( ) or not user.verify_password( form.password.data ):
            return render_template( 'mod_auth/failedlogin.html', form=form )
        login_user( user, form.remember_me.data )
        return redirect( request.args.get( 'next' ) or url_for( 'mod_auth.index' ) )
    temp = render_template( 'mod_auth/login.html', form=form )
    index = temp.find( '</form>' )
    loginform = temp[ :index ] + '<input type="button" class="btn btn-default" id="login_register" value="Register" >' + temp[ index: ]
    return loginform


@mod_auth.route( '/register', methods = [ 'GET', 'POST' ] )
def register():
    form = RegisterForm( )
    if ( form.validate_on_submit( ) and form.password.data == form.confpassword.data ) :
        session = db_session( )

        address = Address( address_1 = form.address1.data,
                           city = form.city.data,
                           state = form.state.data,
                           postcode = form.zip.data )

        address.address_2 = form.address2.data

        session.add( address )
        session.flush( )

        user = User( login_name = form.login_name.data,

                     email = form.email.data
        )

        user.set_password( form.password.data )
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.address_id = address.get_id( )
        user.active = False

        session.add( user )

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