from flask import Blueprint

sequencing = Blueprint('sequencing', __name__, url_prefix = '/sequencing')

from . import routes
