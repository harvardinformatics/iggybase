from flask import redirect, url_for, request, abort
from iggybase.templating import page_template
from flask.ext.login import login_required, login_user, logout_user, current_user
from iggybase.mod_auth.models import User, UserRole, Organization
from iggybase.mod_admin.models import NewUser, Role
from . import mod_auth
from iggybase.mod_auth.forms import LoginForm, RegisterForm
from iggybase.database import admin_db_session
import os
import socket
import json
import logging

@mod_auth.route( '/login', methods = [ 'GET', 'POST' ] )
def login():
    form = LoginForm( )
    if form.validate_on_submit( ):
        user = User.query.filter_by( name=form.name.data ).first( )
        if user is None or not user.is_active( ) or not user.verify_password( form.password.data ):
            return page_template( 'mod_auth/failedlogin', form=form, page_msg = 'Please verify your login credentials or register for an account.' )
        login_user( user, form.remember_me.data )

        if user.home_page is not None:
            return redirect( request.args.get( 'next' ) or url_for( user.home_page, page_type = user.home_page_variable ) )
        else:
            return redirect( request.args.get( 'next' ) ) or abort( 404 )

    return page_template( 'mod_auth/login', form=form )


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

        return page_template( 'mod_auth/regcomplete' )

    return page_template( 'mod_auth/register', form=form )


@mod_auth.route( '/logout' )
def logout():
    logout_user()
    return redirect( url_for( 'mod_auth.login' ) )


@mod_auth.route( '/regcomplete' )
def regcomplete( ):
    return page_template( 'mod_auth/regcomplete', page_msg = 'Thank you for registering. Your registration will be reviewed within 1 business day.'  )


@mod_auth.route( '/registererror' )
def registererror( ):
    return page_template( 'mod_auth/regerror', page_msg = 'Error encountered while registering.' )


@mod_auth.route( '/failedlogin' )
def failedlogin( ):
    return page_template( 'mod_auth/failedlogin', page_msg = 'Please verify your login credentials or register for an account.' )


@mod_auth.route( '/getrole', methods = [ 'POST' ] )
def getrole( ):
    username =  request.json[ 'user' ];
    user = User.query.filter_by( name = username ).first( )
    if user is None:
        return json.dumps( { 'user': 'none', 'roles': { 'none': 'none' }, 'current': { 'role': 'none', 'org': 'none' } } )

    userroles = UserRole.query.filter_by( user_id = user.id ).all( )

    roles = { }
    for userrole in userroles:
        if userrole.role_id not in roles:
            role = Role.query.filter_by( id = userrole.role_id ).first( )
            roles[ userrole.role_id ] = role.name

    currentuserrole = UserRole.query.filter_by( id = user.current_user_role_id ).first( )

    if currentuserrole is None:
        return json.dumps( { 'user': username, 'roles': roles, 'current': { 'role': 'none', 'org': 'none' } } )
    else:
        return json.dumps( { 'user': username, 'roles': roles, 'current': { 'role': currentuserrole.role_id, \
                                                            'org': currentuserrole.organization_id } } )


@mod_auth.route( '/getorganization', methods = [ 'POST' ] )
def getorganization( ):
    username =  request.json[ 'user' ];
    user = User.query.filter_by( name = username ).first( )
    if user is None:
        return json.dumps( { 'user': 'none', 'current': { 'role': 'none', 'org': 'none' }, 'roles': { 'none': 'none' }, \
                             'orgs': { 'none': 'none' } } )

    userroles = UserRole.query.filter_by( user_id = user.id ).all( )

    roles = { }
    orgs = { }
    for userrole in userroles:
        if userrole.role_id not in roles:
            role = Role.query.filter_by( id = userrole.role_id ).first( )
            roles[ userrole.role_id ] = role.name
        if userrole.organization_id not in orgs:
            org = Organization.query.filter_by( id = userrole.organization_id ).first( )
            orgs[ userrole.organization_id ] = org.name

    currentuserrole = UserRole.query.filter_by( id = user.current_user_role_id ).first( )

    if currentuserrole is None:
        return json.dumps( { 'user': username, 'current': { 'role': 'none', 'org': 'none' }, 'roles': roles, 'orgs': orgs } )
    else:
        return json.dumps( { 'user': username, 'current': { 'role': currentuserrole.role_id, \
                                                            'org': currentuserrole.organization_id }, \
                             'roles': roles, 'orgs': orgs } )
