from flask import Blueprint

mod_core = Blueprint( 'mod_core', __name__ )

from . import routes