from flask import Blueprint

murray = Blueprint('murray', __name__, url_prefix = '/<facility_name>/murray')

from . import routes
