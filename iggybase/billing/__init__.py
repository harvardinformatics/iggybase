from flask import Blueprint

billing = Blueprint('billing', __name__)

from . import routes
