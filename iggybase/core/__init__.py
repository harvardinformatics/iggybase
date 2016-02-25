from flask import Blueprint

core = Blueprint('core', __name__, url_prefix = '/<facility_name>/core')

from . import routes
