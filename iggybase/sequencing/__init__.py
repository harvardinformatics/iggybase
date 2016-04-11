from flask import Blueprint

sequencing = Blueprint('sequencing', __name__)

from . import routes
