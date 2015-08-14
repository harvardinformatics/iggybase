from flask import Blueprint

mod_static = Blueprint( 'mod_static', __name__ )

from . import routes