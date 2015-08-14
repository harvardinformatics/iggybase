from flask import render_template, redirect, url_for, request, flash
from flask.ext.login import login_required, login_user, logout_user
from .models import User
from . import mod_auth
from ..mod_core.models import Address
from .forms import LoginForm, RegisterForm
from iggybase.database import db_session

@mod_auth.route( '/login', methods = [ 'GET', 'POST' ] )
def login():
    form = LoginForm( )
    if form.validate_on_submit( ):
        user = User.query.filter_by( username=form.username.data ).first( )
        if user is None or not user.verify_password( form.password.data ):
            return redirect( url_for( 'mod_auth.login', **request.args ) )
        login_user( user, form.remember_me.data )
        return redirect( request.args.get( 'next' ) or url_for( 'mod_auth.index' ) )
    temp = render_template( 'mod_auth/login.html', form=form )
    index = temp.find( '</form>' )
    loginform = temp[ :index ] + '<input type="button" class="btn btn-default" id="login_register" value="Register" >' + temp[ index: ]
    return loginform


@mod_auth.route( '/register', methods = [ 'GET', 'POST' ] )
def register():
    form = RegisterForm( )
    if form.validate_on_submit( ):
        session = db_session( )

        address = Address( address_1 = form.address1.data,
                           address_2 = form.address2.data,
                           city = form.city.data,
                           state = form.state.data,
                           postcode = form.zip.data )
        session.add( address )
        user = User( login_name = form.login_name.data,
                     first_name = form.first.data,
                     last_name = form.last.data,
                     email = form.email.data,
                     address_id = address.address_id,
                     active = False
                     )
        session.add( user )

        user.set_password( form.password.data )
        session.commit

        flash( "Your credentials will be reviewed in 1 business day.")
        return redirect( url_for( 'mod_auth.login' ) )
    return render_template( 'mod_auth/register.html', form=form )


@mod_auth.route( '/logout' )
def logout():
    logout_user()
    return redirect( url_for( 'mod_auth.login' ) )


@mod_auth.route( '/' )
def index( ):
    return render_template( 'index.html' )

