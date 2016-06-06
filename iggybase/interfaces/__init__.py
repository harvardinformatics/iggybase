from flask import Blueprint

interfaces = Blueprint('interfaces', __name__)

from . import routes
