from flask import Blueprint

mod_murray_lab = Blueprint( 'mod_murray_lab', __name__, url_prefix = '/murray' )

from iggybase.mod_murray_lab import routes