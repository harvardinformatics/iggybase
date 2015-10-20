from flask import render_template as renderer
from iggybase.mod_auth.access_control import AccessControl
from iggybase.mod_admin.models import Menu, MenuItem
import logging

def render_template(template_name, **context):
    acctrl = AccessControl( )
    #context[ 'navbar' ] =
    #context[ 'sidebar' ] =

    context[ 'rows' ] = [ ( '1', 'test1' ), ( '2', 'test2' ) ]
    context[ 'headers' ] = [ 'ID', 'Name' ]
    return renderer( template_name, **context )