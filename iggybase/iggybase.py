import os
from collections import OrderedDict
from flask import Flask, g, send_from_directory, abort, url_for, request, \
redirect
from wtforms import StringField, SelectField, ValidationError
from wtforms.validators import DataRequired
from config import config, get_config
from flask import render_template
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, \
RoleMixin, login_required, current_user, LoginForm, RegisterForm, \
user_registered, logout_user
from flask.ext.security.registerable import register_user
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.wsgi import DispatcherMiddleware
from iggybase.extensions import mail, lm, bootstrap
from iggybase.admin import models
from iggybase.database import db, init_db, db_session
import iggybase.auth.role_access_control as rac
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

    configure_blueprints(iggybase, conf.BLUEPRINTS)
    security, user_datastore = configure_extensions( iggybase, db )
    configure_error_handlers( iggybase )
    configure_hook( iggybase )

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
    @security.context_processor
    def security_context_processor():
        return security_menu()

    def security_menu():
        navbar = OrderedDict([('Login', {'title': 'Login', 'url':url_for('security.login')}), ('Register', {'title':'Register', 'url':url_for('register')}),
            ('Reset Password', {'title':'Reset Password', 'url':url_for('security.forgot_password')}), ('Logout', {'title':'Logout', 'url':url_for('security.logout')})])
        return dict(navbar = navbar)

    def get_new_name(model):
        to = (models.TableObject.query.
                filter_by(name=model.__tablename__).first())
        return to.get_new_name()

    def populate_model(model_name, form, extra, set_name = True, prefix = ''):
        obj = getattr(models, model_name)()
        cols = obj.__table__.columns.keys()
        # create dict from keys and add form prefix if any
        # exp for billing address "b_"
        fields = {k: (prefix + k) for k in cols}
        for key, val in fields.items():
            if hasattr(form, val) and hasattr(obj, key):
                new_val = getattr(form, val).data
                # QuerySelectFields save objects, we need id
                if hasattr(new_val, 'id'):
                    new_val = new_val.id
                setattr(obj, key, getattr(form, val).data)
        # add auto name
        if set_name:
            setattr(obj, 'name', get_new_name(obj))
        # add extra non-form values
        for key, val in extra.items():
            if hasattr(obj, key):
                setattr(obj, key, val)
        return obj


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form_class = ExtendedRegisterForm
        form_data = request.form
        form = form_class(form_data)
        if form.validate_on_submit():
            user_dict = form.to_dict()
            user_exists = models.User.query.filter_by(name = user_dict['name']).first()
            org = form.data['organization']
            user_dict['organization_id'] = org
            user = register_user(**user_dict)
            # insert user_org
            user_org = populate_model('UserOrganization',
                    form,
                    {
                        'user_id': user.id,
                        'active': 1,
                        'default_organization': 1,
                        'user_organization_id': org,
                        'organization_id': org
                    }
            )
            db.session.add(user_org)
            # insert role
            level = models.Level.query.filter_by(name = 'User').first()
            role = models.Role.query.filter(
                    models.Role.facility_id == form.facility.data,
                    models.Role.level_id == level.id).first()
            user_datastore.add_role_to_user(user, role)
            db.session.commit()
            # update user address and role
            user_role = (models.UserRole.query.filter_by(user_id = user.id, role_id =
                    role.id).first())
            user.current_user_role_id = user_role.id
            db.session.commit()
            return redirect(url_for('registration_success'))
        ctx = security_menu()
        return render_template('security/register_user.html', register_user_form =
                form, **ctx)

    @app.route( '/registration_success' )
    def registration_success():
        logout_user()
        ctx = security_menu()
        return render_template( 'registration_sucess.html', **ctx)

    @app.route( '/welcome' )
    def welcome():
        return render_template( 'welcome.html')

    @app.after_request
    def remove_session(resp):
        db_session.close()
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

def configure_blueprints(app, blueprints):
    for module in blueprints:
        bp = getattr(__import__('iggybase.'+module, fromlist=[module]),module)
        app.register_blueprint(bp)

def configure_hook( app ):
    @app.before_request
    def before_request():
        g.user = current_user
        g.facility = ""
        path = request.path.split('/')

        # TODO: consider caching this for the session
        ignore_facility = ['static', 'logout', 'home', 'welcome',
        'registration_success']
        if (current_user.is_authenticated and path and path[1] not in
                ignore_facility):
            # set module in g
            if len(path) > 2:
                g.module = path[2]
            role_access = rac.RoleAccessControl()
            g.rac = role_access
            access = role_access.has_facility_access(path[1])

            if not access:
                if path[1] in role_access.facilities:
                    role_access.change_role(role_access.facilities[path[1]])
                else:
                    abort(404)
            g.facility = path[1]

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

# Validators and Forms
def unique_field(obj, attr = 'name', msg = ''):
    # check for unique name
    def _unique_field(form, field):
        model = getattr(models, obj)
        col = getattr(model, attr)
        name = model.query.filter(col ==
                field.data).first()
        if name:
            raise ValidationError('This ' + attr + ' exists please choose a'
            ' different one. ' + msg)
    return _unique_field


class ExtendedLoginForm(LoginForm):
    email = StringField('Username or email:')

class ExtendedRegisterForm(RegisterForm):
    name = StringField('Username:', [DataRequired(), unique_field(obj = 'User')])
    first_name = StringField('First Name:', [DataRequired()])
    last_name = StringField('Last Name:', [DataRequired()])
    msg = 'If your email exists then please reset your password rather than re-register'
    email = StringField('Email:', [DataRequired(), unique_field(obj = 'User',
        attr = 'email', msg = msg)])
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
