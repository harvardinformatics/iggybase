from iggybase.mod_auth.models import UserRole, Organization
from iggybase.mod_admin.models import Role

def get_roles( user_id = None ):
    if user_id is None:
        user_roles = UserRole.query.all( )
    else:
        user_roles = UserRole.query.filter_by( user_id = user_id ).all( )

    if user_roles is None:
        return [ ( 'none', 'none' ) ]

    roles = [ ( 0, '' ) ]
    for user_role in user_roles:
        if user_role.role_id not in roles:
            role = Role.query.filter_by( id = user_role.role_id ).first( )
            option = ( user_role.role_id, role.name )
            roles.append( option )

    return roles

def get_current_user_role( current_user_role_id ):
    current_user_role = UserRole.query.filter_by( id = current_user_role_id ).first( )

    if current_user_role is None:
        return None
    else:
        return current_user_role.role_id

def get_organizations( user_id = None, role_id = None ):
    if user_id is None and role_id is None:
        user_roles = UserRole.query.all( )
    elif user_id is None:
        user_roles = UserRole.query.filter_by( role_id = role_id ).all( )
    elif role_id is None:
        user_roles = UserRole.query.filter_by( user_id = user_id ).all( )
    else:
        user_roles = UserRole.query.filter_by( user_id = user_id ).filter_by( role_id = role_id ).all( )

    if user_roles is None:
        return [ ( 'none', 'none' ) ]

    orgs = [ ( 0, '' ) ]
    for user_role in user_roles:
        if user_role.organization_id not in orgs:
            org = Organization.query.filter_by( id = user_role.organization_id ).first( )
            option = ( user_role.organization_id, org.name )
            orgs.append( option )

    return orgs

def get_current_user_organization( current_user_role_id ):
    current_user_role = UserRole.query.filter_by( id = current_user_role_id ).first( )

    if current_user_role is None:
        return None
    else:
        return current_user_role.organization_id
