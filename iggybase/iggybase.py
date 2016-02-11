import os
from collections import OrderedDict
from flask import Flask, g, send_from_directory, abort
from wtforms import TextField, SelectField
from wtforms.validators import Required
from config import config, get_config
from flask import render_template
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, \
RoleMixin, login_required, current_user, LoginForm, RegisterForm, \
user_registered, logout_user
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.wsgi import DispatcherMiddleware
from iggybase.extensions import mail, lm, bootstrap
from iggybase.mod_admin import models
from iggybase.database import db, init_db, db_session
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
    security, user_datastore = configure_extensions( iggybase, db )
    configure_hook( iggybase )
    configure_error_handlers( iggybase )

    add_base_routes( iggybase, conf, security, user_datastore )



    return iggybase


def configure_extensions( app, db ):
    bootstrap.init_app( app )
    lm.init_app( app )
    mail.init_app( app )


    # configure Flask Security
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security = Security(app, user_datastore, login_form = ExtendedLoginForm,
            register_form = ExtendedRegisterForm)

    return security, user_datastore

def add_base_routes( app, conf, security, user_datastore ):
    from iggybase import base_routes

    @user_registered.connect_via(app)
    def user_registered_sighandler(sender, **extra):
        # TODO: we should dynamically enter facility based on what's in user
        # or perhaps we just need to overide some other function in sqlalchemy
        # for now i'm hardcogin one facility
        user = extra.get('user')
        role = user_datastore.find_or_create_role('new_user', facility_id = 2,
                level_id = 7)
        user_datastore.add_role_to_user(user, role)
        db.session.commit()

    @app.route( '/registration_success' )
    def registration_success():
        logout_user()
        return render_template( 'registration_sucess.html')

    @app.before_request
    def before_request( ):
        modules = [x[0] for x in conf.BLUEPRINTS]

    @app.after_request
    def remove_session(resp):
        db_session.remove()
        return resp

    @app.route( '/index/' )
    @login_required
    def index():
        return base_routes.index()

    @app.route( '/ajax/change_role', methods=['POST'] )
    @login_required
    def change_role():
        return base_routes.change_role()

    @app.route( '/ajax/update_table_rows/<table_name>', methods=['GET', 'POST'] )
    @login_required
    def update_table_rows(table_name):
        return base_routes.update_table_rows(table_name)

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
        navbar = OrderedDict([('Login', {'title': 'Login', 'url':'/login'}), ('Register', {'title':'Register', 'url':'/register'}),
            ('Reset Password', {'title':'Reset Password', 'url':'/reset'}), ('Logout', {'title':'Logout', 'url':'/logout'})])
        return dict(navbar = navbar)

    @app.route( '/<module_name>/<page_form>/<table_name>/' )
    @login_required
    def module_page_table_function(module_name, page_form, table_name):
        try:
            base_function = getattr(base_routes, page_form)
        except AttributeError:
            abort(404)
        return base_function( module_name, table_name )


    @app.route( '/<module_name>/<page_form>/<table_name>/ajax' )
    @login_required
    def module_page_table_function_ajax(module_name, page_form, table_name):
        try:
            base_function = getattr(base_routes, (page_form + '_ajax'))
        except AttributeError:
            abort(404)
        return base_function(module_name, table_name)

    @app.route( '/<module_name>/summary/<table_name>/download/' )
    @login_required
    def summary_download( module_name, table_name ):
        return base_routes.summary_download( module_name, table_name )

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
        return base_routes.multiple_entry( module_name, table_name )

def configure_blueprints( app, blueprints ):
    for i,(module, blueprint) in enumerate(blueprints):
        bp = getattr(__import__('iggybase.'+module, fromlist=[module]),module)
        app.register_blueprint( bp )

def configure_hook( app ):
    @app.before_request
    def before_request():
        g.user = current_user

def configure_error_handlers( app ):
    from iggybase import base_routes

    @app.errorhandler( 403 )
    def forbidden_page(error):
        # we want menus to show up for this error
        return base_routes.forbidden(), 403

    @app.errorhandler( 404 )
    def page_not_found(error):
        return render_template( "errors/page_not_found.html"), 404

    @app.errorhandler( 500 )
    def server_error_page(error):
        return render_template( "errors/server_error.html" ), 500



class ExtendedLoginForm(LoginForm):
    email = TextField('Username or email:')

class ExtendedRegisterForm(RegisterForm):
    name = TextField('Username:', [Required()])
    first_name = TextField('First Name:', [Required()])
    last_name = TextField('Last Name:', [Required()])
    email = TextField('Email:', [Required()])
    organization = TextField('Organization:', [Required()])
    address1 = TextField('Address 1:', [Required()])
    address2 = TextField('Address 2:', [Required()])
    city = TextField('City:', [Required()])
    state = TextField('State:', [Required()])
    zipcode = TextField('Zipcode:', [Required()])
    phone = TextField('Phone:', [Required()])
    organization = SelectField('Organization:', coerce=int)
    facility = SelectField('Service:', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ExtendedRegisterForm, self).__init__(*args, **kwargs)

        orgs = models.Organization.query
        org_choices = []
        for org in orgs:
            org_choices.append((org.id, org.name))
        self.organization.choices = org_choices

        facilities = models.Facility.query
        fac_choices = []
        for fac in facilities:
            fac_choices.append((fac.id, fac.name))
        self.facility.choices = fac_choices
