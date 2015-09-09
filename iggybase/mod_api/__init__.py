from flask import Blueprint

mod_api = Blueprint( 'mod_api', __name__, url_prefix = '/api' )

from . import routes