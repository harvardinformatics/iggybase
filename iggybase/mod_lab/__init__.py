from flask import Blueprint

mod_lab = Blueprint( 'mod_lab', __name__, url_prefix = '/core' )

from iggybase.mod_lab import routes