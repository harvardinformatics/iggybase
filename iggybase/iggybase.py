import os
from collections import OrderedDict
from flask import Flask, g, send_from_directory, abort, url_for, request
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired
from config import Config
from flask import render_template
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, \
RoleMixin, login_required, current_user, LoginForm, RegisterForm, \
user_registered, logout_user
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.wsgi import DispatcherMiddleware
from iggybase.extensions import mail, lm, bootstrap
from iggybase.admin import models
from iggybase.cache import Cache
from iggybase.database import db, init_db, db_session
from event_action import init_app as init_act_mgr
import logging

__all__ = [ 'create_app' ]

def create_app( app_name = None ):
    conf = Config( )
    iggybase = Flask( __name__ )
    iggybase.config.from_object( conf )
    iggybase.cache = Cache()

    if app_name is None:
        app_name = conf.PROJECT

    init_db( )

    configure_blueprints(iggybase)
    security, user_datastore = configure_extensions( iggybase, db )
    configure_error_handlers( iggybase )
    configure_hook( iggybase )

    add_base_routes( iggybase, conf, security, user_datastore )

    return iggybase


def configure_extensions( app, db ):
    bootstrap.init_app( app )
    lm.init_app( app )
    mail.init_app( app )
    init_act_mgr(app, db_session)

    # configure Flask Security
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security = Security(app, user_datastore, login_form = ExtendedLoginForm,
            register_form = ExtendedRegisterForm)

    # Configure actions - the import statement has to be here since it
    # can't preceed the user datastor setup.
    # from iggybase.admin.events import StartEvents
    # StartEvents(app).configure(db_session)

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

    @app.after_request
    def remove_session(resp):
        db_session.remove()
        return resp

    @app.route( '/index/' )
    @login_required
    def index():
        return base_routes.index()

    @app.route( '/home' )
    @login_required
    def home():
        return base_routes.home()

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico')

    @security.context_processor
    def security_context_processor():
        navbar = OrderedDict([('Login', {'title': 'Login', 'url':url_for('security.login')}), ('Register', {'title':'Register', 'url':url_for('security.register')}),
            ('Reset Password', {'title':'Reset Password', 'url':url_for('security.forgot_password')}), ('Logout', {'title':'Logout', 'url':url_for('security.logout')})])
        return dict(navbar = navbar)

def configure_blueprints(app):
    blueprints = models.Module.query.filter_by(blueprint = 1).all()
    for mod in blueprints:
        bp = getattr(__import__('iggybase.'+mod.name, fromlist=[mod.name]),mod.name)
        url_prefix = '/<facility_name>/' + mod.name
        app.register_blueprint(bp, url_prefix = url_prefix)

def configure_hook( app ):
    @app.before_request
    def before_request():
        g.user = current_user
        g.facility = ""

        path = request.path.split('/')

        # TODO: consider caching this for the session
        ignore_facility = ['static', 'logout', 'home', 'favicon.ico']
        if (current_user.is_authenticated and path and path[1] not in ignore_facility):
            import iggybase.core.role_access_control as rac

            # set module in g
            if len(path) > 2:
                g.module = path[2]

            role_access = rac.RoleAccessControl()
            g.rac = role_access
            role_access.set_routes()
            access = role_access.has_facility_access(path[1])
            if not access:
                if path[1] in role_access.facilities:
                    role_access.change_role(role_access.facilities[path[1]])
                else:
                    abort(404)

            g.facility = path[1]
            route_access = role_access.route_access(request.path)

            if not route_access:
                abort(404)

def configure_error_handlers( app ):
    from iggybase import base_routes

    @app.errorhandler( 403 )
    def forbidden_page(error):
        # we want menus to show up for this error
        return base_routes.forbidden(), 403

    @app.errorhandler( 404 )
    def page_not_found(error):
        return base_routes.page_not_found(), 404

    @app.errorhandler( 500 )
    def server_error_page(error):
        return render_template( "errors/server_error.html" ), 500



class ExtendedLoginForm(LoginForm):
    email = StringField('Username or email:')

class ExtendedRegisterForm(RegisterForm):
    name = StringField('Username:', [DataRequired()])
    first_name = StringField('First Name:', [DataRequired()])
    last_name = StringField('Last Name:', [DataRequired()])
    email = StringField('Email:', [DataRequired()])
    organization = StringField('Organization:', [DataRequired()])
    address1 = StringField('Address 1:', [DataRequired()])
    address2 = StringField('Address 2:', [DataRequired()])
    city = StringField('City:', [DataRequired()])
    state = StringField('State:', [DataRequired()])
    zipcode = StringField('Zipcode:', [DataRequired()])
    phone = StringField('Phone:', [DataRequired()])
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


