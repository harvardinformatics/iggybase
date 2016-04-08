from flask import Blueprint

core = Blueprint('core', __name__)

from . import routes
