from flask import g, render_template as renderer
from flask_login import current_user
from iggybase.mod_admin.models import Menu, MenuItem
import logging

def render_template(template_name, **context):
    g.user = current_user
    #context[ 'navbar' ] =
    #context[ 'sidebar' ] =

    context[ 'rows' ] = [ ( '1', 'test1' ), ( '2', 'test2' ) ]
    context[ 'headers' ] = [ 'ID', 'Name' ]
    return renderer( template_name, **context )