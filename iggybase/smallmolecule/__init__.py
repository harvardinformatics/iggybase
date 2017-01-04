from flask import Blueprint

smallmolecule = Blueprint('smallmolecule', __name__)

from . import routes
