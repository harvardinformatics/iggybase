from flask import Blueprint

mod_murray = Blueprint( 'mod_murray', __name__, url_prefix = '/<facility_name>/murray' )

from iggybase.mod_murray import routes
