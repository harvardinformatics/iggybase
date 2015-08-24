from flask import render_template as Renderer
from flask_login import current_user
from iggybase.mod_admin.models import Lab, Menu, MenuItem
import logging

def render_template(template_name_or_list, **context):
    #context[ 'navbar' ] =
    #context[ 'sidemenu' ] =

    return Renderer( template_name_or_list, **context )