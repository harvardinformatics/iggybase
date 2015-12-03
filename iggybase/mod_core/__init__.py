from flask import Blueprint

mod_core = Blueprint( 'mod_core', __name__, url_prefix = '/core' )

from . import routes