from flask import Blueprint

laboratory = Blueprint('laboratory', __name__)

from . import routes
