from flask import render_template as Renderer
from flask_login import current_user
from iggybase.mod_admin.models import Lab, Menu, Menu_Item
from iggybase.mod_auth.models import User, load_user
import logging

def render_template(template_name_or_list, **context):
    userid = current_user.get_id( )

    logging.info( 'userid: ' + str( userid ) )
    #context[ 'navbar' ] =
    #context[ 'sidemenu' ] =

    return Renderer( template_name_or_list, context )