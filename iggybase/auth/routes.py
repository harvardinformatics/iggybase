from flask import redirect, url_for, request, abort, g
from flask_security.decorators import login_required
from iggybase.admin.models import User
from . import auth
from iggybase.auth.role_organization import get_roles, get_organizations, get_current_user_role, \
    get_current_user_organization
import json
import logging

@auth.route( '/getrole', methods = [ 'POST' ] )
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


@auth.route( '/getorganization', methods = [ 'POST' ] )
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

