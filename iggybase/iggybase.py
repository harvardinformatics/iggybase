import os
from flask import Flask, g, send_from_directory
from wtforms import TextField
from wtforms.validators import Required
from config import config, get_config
from flask import render_template
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, \
RoleMixin, login_required, current_user, LoginForm, RegisterForm
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.wsgi import DispatcherMiddleware
from iggybase.extensions import mail, lm, bootstrap
from iggybase.mod_admin import models
from iggybase.database import db, init_db
import logging

__all__ = [ 'create_app' ]

def create_app( config_name = None, app_name = None ):
    if config_name is None:
        conf = get_config( )
    else:
        conf = config[ config_name ]( )

    iggybase = Flask( __name__ )
    iggybase.config.from_object( conf )

    if app_name is None:
        app_name = conf.PROJECT

    init_db( )

    configure_blueprints( iggybase, conf.BLUEPRINTS )
    security = configure_extensions( iggybase, db )
    configure_hook( iggybase )
    configure_error_handlers( iggybase )

    add_base_routes( iggybase, conf, security )

    return iggybase


def configure_extensions( app, db ):
    bootstrap.init_app( app )
    lm.init_app( app )
    mail.init_app( app )


    # configure Flask Security
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security = Security(app, user_datastore, login_form = ExtendedLoginForm,
            register_form = ExtendedRegisterForm)

    return security

def add_base_routes( app, conf, security ):
    from iggybase import base_routes

    @app.before_request
    def before_request( ):
        modules = [x[0] for x in conf.BLUEPRINTS]

    @app.route( '/index/' )
    @login_required
    def index():
        return base_routes.index()

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico')

    @app.route( '/<module_name>/' )
    @login_required
    def default(module_name):
        return base_routes.default()

    @security.context_processor
    def security_context_processor():
        navbar = {'Login':{'url':'/login'}, 'Register':{'url':'/register'},
                'Reset Password':{'url':'/reset'}, 'Logout':{'url':'/logout'}}
        return dict(navbar = navbar)

    @app.route( '/<module_name>/summary/<table_name>/' )
    @login_required
    def summary( module_name, table_name ):
        return base_routes.summary( module_name, table_name )

    @app.route( '/<module_name>/summary/<table_name>/ajax' )
    @login_required
    def summary_ajax(module_name, table_name):
        return base_routes.summary_ajax(module_name, table_name)

    @app.route( '/<module_name>/summary/<table_name>/download/' )
    @login_required
    def summary_download( module_name, table_name ):
        return base_routes.summary_download( module_name, table_name )

    @app.route( '/<module_name>/action_summary/<table_name>/' )
    @login_required
    def action_summary( module_name, table_name ):
        return base_routes.action_summary( module_name, table_name )

    @app.route( '/<module_name>/action_summary/<table_name>/ajax' )
    @login_required
    def action_summary_ajax( module_name, table_name ):
        return base_routes.action_summary_ajax( module_name, table_name )

    @app.route( '/<module_name>/detail/<table_name>/<row_name>/' )
    @login_required
    def detail( module_name, table_name, row_name ):
        return base_routes.detail( module_name, table_name, row_name )

    @app.route( '/<module_name>/data_entry/<table_name>/<row_name>/', methods=['GET', 'POST'] )
    @login_required
    def data_entry( module_name, table_name, row_name ):
        return base_routes.data_entry( module_name, table_name, row_name )

    @app.route( '/<module_name>/multiple_entry/<table_name>/', methods=['GET', 'POST'] )
    @login_required
    def multiple_entry( module_name, table_name ):
        return base_routes.multiple_data_entry( module_name, table_name )

def configure_blueprints( app, blueprints ):
    for i,(module, blueprint) in enumerate(blueprints):
        bp = getattr(__import__('iggybase.'+module, fromlist=[module]),module)
        app.register_blueprint( bp )

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
        return render_template( "errors/page_not_found.html"), 404

    @app.errorhandler( 500 )
    def server_error_page(error):
        return render_template( "errors/server_error.html" ), 500

class ExtendedLoginForm(LoginForm):
    email = TextField('Username:', [Required()])

class ExtendedRegisterForm(RegisterForm):
    name = TextField('Username:', [Required()])
