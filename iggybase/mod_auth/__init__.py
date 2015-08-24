from flask import Blueprint

mod_auth = Blueprint( 'mod_auth', __name__, url_prefix = '/auth' )

from . import routes