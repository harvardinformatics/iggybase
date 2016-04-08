from flask import Blueprint

murray = Blueprint('murray', __name__)

from . import routes
