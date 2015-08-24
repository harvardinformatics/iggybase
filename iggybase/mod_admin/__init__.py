from flask import Blueprint

mod_admin = Blueprint( 'mod_admin', __name__, url_prefix = '/admin' )

from . import routes