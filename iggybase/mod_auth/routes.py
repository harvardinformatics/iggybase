from flask import redirect, url_for, request, abort, g
from flask_security.decorators import login_required
from iggybase.mod_admin.models import User
from . import mod_auth
from iggybase.mod_auth.role_organization import get_roles, get_organizations, get_current_user_role, \
    get_current_user_organization
import json
import logging


@mod_auth.route('/home', methods=['GET'])
@login_required
def home():
    """redirects to user home page
    """
    if not g.user:
        abort( 403 )
    if g.user.home_page:
        home_page = g.user.home_page
    else:
        home_page = '/auth/detail/user/' + g.user.name
        module_name = request.path.split('/')[1]
    return redirect( home_page )


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

