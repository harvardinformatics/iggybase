from flask import render_template as renderer
from iggybase.mod_auth.group_role_access_control import GroupRoleAccessControl
from iggybase.mod_admin.models import Menu, MenuItem
import logging

def render_template(template_name, **context):
    acctrl = GroupRoleAccessControl( )
    #context[ 'navbar' ] =
    #context[ 'sidebar' ] =

    context[ 'rows' ] = [ ( '1', 'test1' ), ( '2', 'test2' ) ]
    context[ 'headers' ] = [ 'ID', 'Name' ]
    return renderer( template_name, **context )