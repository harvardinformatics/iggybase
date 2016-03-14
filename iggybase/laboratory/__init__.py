from flask import Blueprint

laboratory = Blueprint('laboratory', __name__, url_prefix = '/laboratory')

from . import routes
