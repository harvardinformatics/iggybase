import os, logging, sys
import time
from collections import OrderedDict
from flask import Flask, g, send_from_directory, abort, url_for, request
from flask import redirect
from wtforms import StringField, SelectField, ValidationError
from wtforms.validators import DataRequired, Email
from wtforms.ext.sqlalchemy.orm import model_form
from flask_wtf import Form
from config import Config
from flask import render_template
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, \
RoleMixin, login_required, current_user, LoginForm, RegisterForm, \
logout_user
from flask.ext.security.registerable import register_user
from iggybase.extensions import mail, lm, bootstrap
from iggybase.admin import models
from iggybase.cache import Cache
from iggybase import utilities as util
from iggybase.database import db, init_db, db_session

__all__ = [ 'create_app' ]

def create_app():
    conf = Config( )
    iggybase = Flask( __name__ )
    iggybase.config.from_object( conf )
    iggybase.cache = Cache()

    init_db( )

    configure_blueprints(iggybase)
    security, user_datastore = configure_extensions( iggybase, db )
    configure_error_handlers( iggybase )

    add_base_routes(iggybase, conf, security, user_datastore)
    configure_hook( iggybase )

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'iggybase.log'))

    logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                              'iggybase.log'), level=logging.DEBUG)

    return iggybase


def configure_extensions( app, db ):
    bootstrap.init_app( app )
    lm.init_app( app )
    mail.init_app( app )
    #init_act_mgr(app, db_session)

    # configure Flask Security
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security = Security(app, user_datastore, login_form = ExtendedLoginForm,
            register_form = ExtendedRegisterForm)

    # Configure actions - the import statement has to be here since it
    # can't preceed the user data setup.
    # from iggybase.admin.events import StartEvents
    # StartEvents(app).configure(db_session)

    # add button function to jinja
    app.add_template_global(util.html_button, name='html_button')

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

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form_class = ExtendedRegisterForm
        form_data = request.form
        form = form_class(form_data)
        if form.validate_on_submit():
            user_dict = form.to_dict()
            # ensure new accounts are unverified
            user_dict['verified'] = 0
            user = register_user(**user_dict)
            level = models.Level.query.filter_by(name = 'User').first()
            role = models.Role.query.filter(
                    models.Role.facility_id == form.facility.data,
                    models.Role.level_id == level.id).first()
            user_datastore.add_role_to_user(user, role)
            db.session.commit()
            return redirect(url_for('registration_success'))
        ctx = security_menu()
        return render_template('security/register_user.html', register_user_form =
                form, **ctx)

    @app.route( '/registration_success' )
    def registration_success():
        logout_user()
        ctx = security_menu()
        return render_template('registration_sucess.html', **ctx)

    @app.route('/new_group', methods=['GET', 'POST'])
    def new_group():
        form_data = request.form
        form_class = model_form(models.Organization, db_session=db_session,
                base_class=Form,
                only=['name', 'description'],
                field_args={
                    'name':{'validators':[DataRequired(), unique_name]}
                    },
                type_name='New Group'
        )
        form = form_class(form_data)
        if form.validate_on_submit():
            user_dict = form.to_dict()
            # ensure new accounts are unverified
            user_dict['verified'] = 0
            user = register_user(**user_dict)
            level = models.Level.query.filter_by(name = 'User').first()
            role = models.Role.query.filter(
                    models.Role.facility_id == form.facility.data,
                    models.Role.level_id == level.id).first()
            user_datastore.add_role_to_user(user, role)
            db.session.commit()
            return redirect(url_for('registration_success'))
        ctx = security_menu()
        return render_template('dynamic_model_form.html', form =
                form, action='new_group', **ctx)


    @app.route( '/welcome' )
    def welcome():
        return render_template( 'welcome.html')

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

def configure_blueprints(app):
    blueprints = models.Module.query.filter_by(blueprint = 1).all()
    for mod in blueprints:
        bp = getattr(__import__('iggybase.'+mod.name, fromlist=[mod.name]),mod.name)
        url_prefix = '/<facility_name>/' + mod.name
        app.register_blueprint(bp, url_prefix = url_prefix)

def configure_hook( app ):
    @app.before_request
    def before_request():
        start = time.time()
        g.user = current_user
        g.facility = ""
        # TODO: consider caching this for the session
        if (current_user.is_authenticated):
            import iggybase.core.role_access_control as rac
            role_access = rac.RoleAccessControl()
            g.rac = role_access
            path = list(filter(bool, request.path.split('/')))
            # always allow some paths
            ignore_facility = ['static', 'logout', 'favicon.ico', 'welcome', 'registration_success', 'home']
            if path and path[0] in ignore_facility:
                return
            if len(path) < 2: # if no facility or no module send home
                return redirect(url_for('home'))
            else: # check access
                access = role_access.is_current_facility(path[0])
                logging.info('Facility access: ' + str(access))
                if not access:
                    if path[0] in role_access.facilities:
                        role_access.change_role(role_access.facilities[path[0]]['top_role'])
                    else:
                        abort(404)
                g.facility = path[0]
                route_access = role_access.route_access(path)
                print('Route access: ' + str(route_access))
                if not route_access:
                    abort(404)
        current = time.time()
        print('before_request:' + str(current - start))

def configure_error_handlers( app ):
    from iggybase import base_routes

    @app.errorhandler( 403 )
    @login_required
    def forbidden_page(error):
        # we want menus to show up for this error
        return base_routes.forbidden(), 403

    @app.errorhandler( 404 )
    @login_required
    def page_not_found(error):
        return base_routes.page_not_found(), 404

    @app.errorhandler( 500 )
    @login_required
    def server_error_page(error):
        return render_template( "errors/server_error.html" ), 500

# Validators and Forms
def unique_name(obj):
    # check for unique name
    def _unique_name(form, field):
        model = getattr(models, obj)
        name = model.query.filter(model.name ==
                field.data).first()
        if name:
            raise ValidationError('This name exists please choose a'
            ' different one.')
    return _unique_name


class ExtendedLoginForm(LoginForm):
    email = StringField('Username or email:')

class ExtendedRegisterForm(RegisterForm):
    def ints_but_first(x):
        if x == '':
            return ''
        else:
            return int(x)
    name = StringField('Username', [DataRequired(), unique_name(obj = 'User')])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    email = StringField('Email', [DataRequired(), Email()])
    address1 = StringField('Address 1', [DataRequired()])
    address2 = StringField('Address 2', )
    city = StringField('City', [DataRequired()])
    state = StringField('State', [DataRequired()])
    zipcode = StringField('Zipcode', [DataRequired()])
    phone = StringField('Phone')
    organization = SelectField('Group/ PI',
            [DataRequired()], coerce = ints_but_first)
    facility = SelectField('Facility', [DataRequired()], coerce=ints_but_first)

    def __init__(self, *args, **kwargs):
        super(ExtendedRegisterForm, self).__init__(*args, **kwargs)

        orgs = (models.Organization.query.filter(
                models.Organization.organization_type_id != 1,
                models.Organization.public == 1)
            .order_by(models.Organization.name).all())
        org_choices = [('', '')]
        for org in orgs:
            org_choices.append((org.id, org.name))
        self.organization.choices = org_choices

        facilities = models.Facility.query.filter(models.Facility.public == 1).all()
        fac_choices = [('', '')]
        for fac in facilities:
            fac_choices.append((fac.id, fac.name))
        self.facility.choices = fac_choices

