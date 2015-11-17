from flask import Blueprint

mod_lab = Blueprint( 'mod_murray_lab', __name__, url_prefix = '/lab' )

from iggybase.mod_murray_lab import routes