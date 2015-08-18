from flask import Blueprint

mod_admin = Blueprint( 'mod_admin', __name__ )

from . import routes