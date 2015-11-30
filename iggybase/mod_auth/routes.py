from flask import redirect, url_for, request, abort, g
from iggybase.templating import page_template
from flask.ext.login import login_required, login_user, logout_user, current_user
from iggybase.mod_auth.models import User, UserRole
from iggybase.mod_admin.models import NewUser, Role
from . import mod_auth
from iggybase.mod_auth.role_organization import get_roles, get_organizations, get_current_user_role, \
    get_current_user_organization
from iggybase.mod_auth.forms import LoginForm, RegisterForm
from iggybase.database import admin_db_session, db_session
from iggybase.form_generator import FormGenerator
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
import os
import socket
import json
import logging

@mod_auth.before_request
def before_request():
    g.user = current_user

@mod_auth.route( '/login', methods = [ 'GET', 'POST' ] )
def login():
    form = LoginForm( )

    user = User.query.filter_by( name=form.name.data ).first( )

    if user is not None:
        form.role.choices = get_roles( user.id )
        form.organization.choices = get_organizations( user.id, form.role.data )

    if form.validate_on_submit( ):
        user = User.query.filter_by( name = form.name.data ).first( )
        if user is None or not user.is_active or not user.verify_password( form.password.data ):
            return redirect( url_for( 'mod_auth.failedlogin' ) )

        user_role = UserRole.query.filter_by( role_id = form.role.data ). \
            filter_by( organization_id = form.organization.data ).first( )
        user.current_user_role_id = user_role.id

        db_session( ).add( user )
        db_session( ).commit( )

        login_user( user, form.remember_me.data )

        if request.args.get( 'next' ) is not None:
            return redirect( request.args.get( 'next' ) )
        elif user.home_page is not None:
            args = { 'table_object': 'Address', 'row_name': 'new' }
            return redirect( user.home_page )
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
        newuser.organization = form.organization.data
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
    user_name =  request.json[ 'user' ]

    user = User.query.filter_by( name = user_name ).first( )

    if user is None:
        return json.dumps( { 'user': 'none', 'roles': [ ( '0', '' ) ], 'current_role': 'none' } )

    roles = get_roles( user.id )

    current_user_role = get_current_user_role( user.current_user_role_id )

    if current_user_role is None:
        return json.dumps( { 'user': user_name, 'roles': roles, 'current_role': 'none' } )
    else:
        orgs = get_organizations( user.id, current_user_role )

        current_user_org = get_current_user_organization( user.current_user_role_id )

        return json.dumps( { 'user': user_name, 'roles': roles, 'orgs': orgs, 'current_role': current_user_role, \
                             'current_organization': current_user_org} )


@mod_auth.route( '/getorganization', methods = [ 'POST' ] )
def getorganization( ):
    user_name =  request.json[ 'user' ]
    role_id =  request.json[ 'role' ]

    user = User.query.filter_by( name = user_name ).first( )

    if user is None:
        return json.dumps( { 'user': 'none', 'orgs': [ ( '0', '' ) ], 'current_organization': 'none' } )

    orgs = get_organizations( user.id, role_id )

    current_user_org = get_current_user_organization( user.current_user_role_id )

    if current_user_org is None:
        return json.dumps( { 'user': user_name, 'orgs': orgs, 'current_organization': 'none' } )
    else:
        return json.dumps( { 'user': user_name, 'orgs': orgs, 'current_organization': current_user_org } )


@mod_auth.route( '/data_entry/<table_object>/<row_name>' )
def auth_data_entry( table_object = None, row_name = None ):
    fg = FormGenerator( 'mod_auth', table_object )
    form = fg.default_single_entry_form( row_name )

    if form.validate_on_submit( ):
        pass

    return page_template( 'single_data_entry', form = form )



@mod_auth.route( '/summary/<table_name>' )
def summary( table_name = None ):
    organization_access_control = OrganizationAccessControl( 'mod_auth' )
    table_rows = organization_access_control.get_summary_data( table_name )
    return page_template( 'summary', table_name = table_name, table_rows =
            table_rows )

@mod_auth.route( '/detail/<table_name>/<row_name>' )
def detail( table_name = None, row_name= None ):
    organization_access_control = OrganizationAccessControl( 'mod_auth' )
    table_rows = organization_access_control.get_summary_data( table_name, row_name )
    # pass some context for the button to create urls
    mod = request.path.split('/')[1]
    button_context = {'mod': mod, 'table': table_name, 'row_name': row_name}
    return page_template( 'detail', table_name = table_name, row_name = row_name, table_rows = table_rows, button_context=button_context)
