import os, logging, sys
import time
from collections import OrderedDict
from flask import Flask, g, send_from_directory, abort, url_for, request
from flask import redirect, flash
from wtforms import StringField, SelectField, ValidationError, BooleanField
from wtforms.validators import DataRequired, Email
from wtforms.ext.sqlalchemy.orm import model_form, QuerySelectField
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
            # ensure new accounts are unverified
            user_dict['verified'] = 0
            org = form.data['organization'].id
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
            # insert address
            address = populate_model('Address', form, {'active': 1,
                'organization_id': org})
            db.session.add(address)
            # insert role
            level = models.Level.query.filter_by(name = 'User').first()
            role = models.Role.query.filter(
                    models.Role.facility_id == form.facility.data.id,
                    models.Role.level_id == level.id).first()
            user_datastore.add_role_to_user(user, role)
            db.session.commit()
            # update user address and role
            user.address_id = address.id
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
        return render_template('registration_sucess.html', **ctx)

    @app.route('/new_group', methods=['GET', 'POST'])
    def new_group():
        form_data = request.form
        form = NewGroupForm(form_data)
        if form.validate_on_submit():
            root_org = form.data['facility'].root_organization_id
            org = populate_model('Organization',
                    form,
                    {
                        'organization_id': root_org,
                        'parent_id': root_org,
                        'active': 0,
                        'public': 1,
                        'organization_type_id':
                        form.data['organization_type'].id,
                        # TODO: we should find a way to get these automoatically
                        'department_id': getattr(form.data['department'], 'id',
                            None),
                        'institution_id': getattr(form.data['institution'],
                            'id', None)
                    },
                    False
            )
            db.session.add(org)
            db.session.commit()
            # insert address
            address = populate_model('Address', form, {'active': 1,
                'organization_id': org.id})
            db.session.add(address)
            db.session.commit()
            main_addr = address.id
            if getattr(form, 'same_as_above').data == False:
                # insert billing address
                address = populate_model('Address', form, {'active': 1, 'organization_id': org.id}, True, 'b_')
                db.session.add(address)
                db.session.commit()
            # set to billing address or default to address
            org.billing_address_id = address.id
            org.address_id = main_addr
            db.session.commit()
            flash('New group ' + org.name + ' added.')
            return redirect(url_for('register'))
        ctx = security_menu()
        return render_template('new_group.html', form =
                form, **ctx)


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
def unique_field(obj, attr = 'name'):
    # check for unique name
    def _unique_field(form, field):
        model = getattr(models, obj)
        col = getattr(model, attr)
        name = model.query.filter(col ==
                field.data).first()
        if name:
            raise ValidationError('This name exists please choose a'
            ' different one.')
    return _unique_field

class ElseRequired(DataRequired):
    def __init__(self, attr, *args, **kwargs):
        self.attr = attr
        super(ElseRequired, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        if getattr(form, self.attr).data == False:
            super(ElseRequired, self).__call__(form, field)

def get_facility_select():
    def fac_opts():
        return models.Facility.query.filter(models.Facility.public ==
        1).order_by(models.Facility.name)

    return QuerySelectField('Facility', [DataRequired()],
            query_factory=fac_opts, allow_blank=True)

class ExtendedLoginForm(LoginForm):
    email = StringField('Username or email:')

class ExtendedRegisterForm(RegisterForm):
    def org_opts():
        return (models.Organization.query.filter(
                models.Organization.organization_type_id != 1,
                models.Organization.public == 1)
            .order_by(models.Organization.name).all())

    name = StringField('Username', [DataRequired(), unique_field(obj = 'User')])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    email = StringField('Email', [DataRequired(), Email(), unique_field(obj=
    'User', attr = 'email')])
    address_1 = StringField('Address line 1', [DataRequired()])
    address_2 = StringField('Address line 2')
    address_3 = StringField('Address line 3')
    city = StringField('City', [DataRequired()])
    state = StringField('State', [DataRequired()])
    postcode = StringField('Zipcode', [DataRequired()])
    phone = StringField('Phone')
    country = StringField('Country')
    organization = QuerySelectField('Group/ PI', [DataRequired()],
            query_factory= org_opts, allow_blank = True)
    facility = get_facility_select()

# dynamic form using modal_form, base for NewGroupForm
group_form = model_form(models.Organization, db_session=db_session,
        base_class=Form,
        only=['name', 'description', 'organization_type', 'institution',
            'department'],
        field_args={
            'name':{'validators':[DataRequired(), unique_field(obj='Organization')]},
            'organization_type':{'validators':[DataRequired()]}
            },
        type_name='New Group'
)

class NewGroupForm(group_form):
    facility = get_facility_select()

    # Mailing address
    address_1 = StringField('Address line 1', [DataRequired()])
    address_2 = StringField('Address line 2', )
    address_3 = StringField('Address line 3', )
    city = StringField('City', [DataRequired()])
    state = StringField('State', [DataRequired()])
    postcode = StringField('Zipcode', [DataRequired()])
    phone = StringField('Phone')
    country = StringField('Country')

    # Billing address
    same_as_above = BooleanField('Same as above')
    b_address_1 = StringField('Address line 1', [ElseRequired(attr = 'same_as_above')])
    b_address_2 = StringField('Address line 2', )
    b_address_3 = StringField('Address line 2', )
    b_city = StringField('City', [ElseRequired(attr = 'same_as_above')])
    b_state = StringField('State', [ElseRequired(attr = 'same_as_above')])
    b_postcode = StringField('Zipcode', [ElseRequired(attr = 'same_as_above')])
    b_phone = StringField('Phone')
    b_country = StringField('Country')

