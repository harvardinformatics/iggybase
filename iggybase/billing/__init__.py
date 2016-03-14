from flask import Blueprint

billing = Blueprint('billing', __name__, url_prefix = '/billing')

from . import routes
