from flask import Flask, g
from config import config, get_config
from flask import render_template
from flask.ext.login import login_required, current_user
from iggybase.extensions import mail, lm, bootstrap
from iggybase.mod_auth import mod_auth as mod_auth_blueprint
from iggybase.mod_murray import mod_murray as mod_murray_lab_blueprint
from iggybase.mod_admin import mod_admin as mod_admin_blueprint
from iggybase.mod_api import mod_api as mod_api_blueprint
from iggybase.mod_core import mod_core as mod_core_blueprint
from iggybase import base_routes

__all__ = [ 'create_app' ]

DEFAULT_BLUEPRINTS = (
    mod_admin_blueprint,
    mod_core_blueprint,
    mod_auth_blueprint,
    mod_api_blueprint,
    mod_murray_lab_blueprint
)


def create_app( config_name = None, app_name = None ):
    if config_name is None:
        conf = get_config( )
    else:
        conf = config[ config_name ]( )

    blueprints = DEFAULT_BLUEPRINTS

    iggybase = Flask( __name__ )
    iggybase.config.from_object( conf )

    @iggybase.route( '/index' )
    def index():
        render_template( 'index.html' )

    if app_name is None:
        app_name = conf.PROJECT

    from iggybase.database import init_db
    init_db( )

    configure_blueprints( iggybase, blueprints )
    configure_extensions( iggybase )
    configure_hook( iggybase )
    configure_error_handlers( iggybase )

    add_base_routes( iggybase )

    return iggybase


def configure_extensions( app ):
    bootstrap.init_app( app )
    lm.init_app( app )
    mail.init_app( app )


def add_base_routes( app ):
    @app.route( '/<module_name>/' )
    @login_required
    def default(module_name):
        return base_routes.default()

    @app.route( '/<module_name>/summary/<table_name>' )
    @login_required
    def summary( module_name, table_name ):
        return base_routes.summary( module_name, table_name )

    @app.route( '/<module_name>/summary/<table_name>/download' )
    @login_required
    def summary_download( module_name, table_name ):
        return base_routes.summary_download( module_name, table_name )

    @app.route( '/<module_name>/action_summary/<table_name>' )
    @login_required
    def action_summary( module_name, table_name ):
        return base_routes.action_summary( module_name, table_name )

    @app.route( '/<module_name>/detail/<table_name>/<row_name>' )
    @login_required
    def detail( module_name, table_name, row_name ):
        return base_routes.detail( module_name, table_name, row_name )

    @app.route( '/<module_name>/data_entry/<table_name>/<row_name>', methods=['GET', 'POST'] )
    @login_required
    def data_entry( module_name, table_name, row_name ):
        return base_routes.data_entry( module_name, table_name, row_name )

    @app.route( '/<module_name>/multiple_entry/<table_name>', methods=['GET', 'POST'] )
    @login_required
    def multiple_entry( module_name, table_name ):
        return base_routes.multiple_data_entry( module_name, table_name )


def configure_blueprints( app, blueprints ):

    for blueprint in blueprints:
        app.register_blueprint( blueprint )


def configure_hook( app ):
    @app.before_request
    def before_request():
        g.user = current_user


def configure_error_handlers( app ):

    @app.errorhandler( 403 )
    def forbidden_page(error):
        return render_template( "errors/forbidden_page.html" ), 403

    @app.errorhandler( 404 )
    def page_not_found(error):
        return render_template( "errors/page_not_found.html" ), 404

    @app.errorhandler( 500 )
    def server_error_page(error):
        return render_template( "errors/server_error.html" ), 500
