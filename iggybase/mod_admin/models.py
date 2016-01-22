from iggybase.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship, relation, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.security import UserMixin, RoleMixin
from iggybase.mod_admin.constants import ROLE
from iggybase.extensions import lm
import datetime


class Facility(Base):
    __tablename__ = 'facility'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)


class FacilityRole(Base):
    __tablename__ = 'facility_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_id = Column(Integer, ForeignKey('facility.id'))
    role_id = Column(Integer, ForeignKey('role.id'))

    facility_role_facility = relationship("Facility", foreign_keys=[facility_id])
    facility_role_role = relationship("Role", foreign_keys=[role_id])
    facility_role_unq = UniqueConstraint('facility_id', 'role_id')

    def __repr__(self):
        return "<FacilityRole=%s, description=%s, id=%d, role=%s, facility=%s>)" % \
               (self.name, self.description, self.id,
                self.facility_role_role.name, self.facility_role_facility.name)


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('menu.id'))
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    menu_type_id = Column(Integer, ForeignKey('menu_type.id'))

    parent = relationship('Menu', remote_side=[id])
    children = relationship('Menu')
    menu_menu_type = relationship("MenuType", foreign_keys=[menu_type_id])

    def __repr__(self):
        return "<Menu(name=%s, description=%s, id=%d)>" % \
               (self.name, self.description, self.id)


class MenuFacilityRole(Base):
    __tablename__ = 'menu_facility_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_role_id = Column(Integer, ForeignKey('facility_role.id'))
    menu_id = Column(Integer, ForeignKey('menu.id'))
    menu_class = Column(String(100))

    menu_facility_role_facility = relationship(
            "FacilityRole", foreign_keys=[facility_role_id])
    menu_facility_role_unq = UniqueConstraint('facility_role_id', 'menu_id')
    menu_facility_role_menu = relationship("Menu", foreign_keys=[menu_id])

    def __repr__(self):
        return "<MenuFacilityRole(name=%s, description=%s, id=%d, menu_id=%d, order=%d>)" % \
               (self.name, self.description, self.id, self.menu_id, self.order)


class MenuType(Base):
    __tablename__ = 'menu_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)

    def __repr__(self):
        return "<MenuType(name=%s, description=%s, id=%d>)" % \
               (self.name, self.description, self.id)


class MenuUrl(Base):
    """Matches a url to a menu. One to many relationship with Menu.
    """
    __tablename__ = 'menu_url'
    id = Column(Integer, primary_key=True)

    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    menu_id = Column(Integer, ForeignKey('menu.id'))

    url_path = Column(String(512), unique=True)
    url_params = Column(String(1024))  ## Stored as JSON

    menu_url_menu = relationship("Menu", foreign_keys=[menu_id])

    def __repr__(self):
        return "<MenuUrl(name=%s, description=%s, id=%d, url_path=%s>)" % \
               (self.name, self.description, self.id, self.url_path)


class PageForm(Base):
    __tablename__ = 'page_form'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    page_title = Column(String(50))
    page_header = Column(String(50))
    page_template = Column(String(100))


class PageFormJavaScript(Base):
    __tablename__ = 'page_form_javascript'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    page_form_id = Column(Integer, ForeignKey('page_form.id'))
    page_javascript = Column(String(100))

    page_javascript_page = relationship("PageForm", foreign_keys=[page_form_id])


class PageFormFacilityRole(Base):
    __tablename__ = 'page_form_facility_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_role_id = Column(Integer, ForeignKey('facility_role.id'))
    page_form_id = Column(Integer, ForeignKey('page_form.id'))

    page_facility_role_facility = relationship("FacilityRole", foreign_keys=[facility_role_id])
    page_facility_role_page = relationship("PageForm", foreign_keys=[page_form_id])


class PageFormButton(Base):
    __tablename__ = 'page_form_button'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    page_form_id = Column(Integer, ForeignKey('page_form.id'))
    button_type = Column(String(100))
    button_location = Column(String(100))
    button_class = Column(String(100))
    button_value = Column(String(100))
    button_id = Column(String(100))
    special_props = Column(String(255))

    page_form_button_page_form = relationship("PageForm", foreign_keys=[page_form_id])


class PageFormButtonFacilityRole(Base):
    __tablename__ = 'page_form_button_facility_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_role_id = Column(Integer, ForeignKey('facility_role.id'))
    page_form_button_id = Column(Integer, ForeignKey('page_form_button.id'))

    page_form_button_facility_role_facility = relationship("FacilityRole", foreign_keys=[facility_role_id])
    page_form_button_facility_role_page_form = relationship("PageFormButton", foreign_keys=[page_form_button_id])


class TableObject(Base):
    __tablename__ = 'table_object'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)


class TableObjectName(Base):
    __tablename__ = 'table_object_name'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_id = Column(Integer, ForeignKey('facility.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    new_name_prefix = Column(String(100))
    new_name_id = Column(Integer)
    id_length = Column(Integer)

    table_object_table_object_name = relationship("TableObject", foreign_keys=[table_object_id])
    facility_table_object_name = relationship("Facility", foreign_keys=[facility_id])

    def get_new_name(self):
        new_name = self.new_name_prefix + str(self.new_name_id).zfill(self.id_length)
        self.new_name_id += 1
        return new_name


class TableObjectFacilityRole(Base):
    __tablename__ = 'table_object_facility_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_role_id = Column(Integer, ForeignKey('facility_role.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    module_id = Column(Integer, ForeignKey('module.id'))

    type_facility_role_facility = relationship("FacilityRole", foreign_keys=[facility_role_id])
    type_facility_role_type = relationship("TableObject", foreign_keys=[table_object_id])
    type_facility_role_module = relationship("Module", foreign_keys=[module_id])
    type_facility_role_unq = UniqueConstraint('facility_role_id', 'table_object_id')


class TableObjectChildren(Base):
    __tablename__ = 'table_object_children'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    child_table_object_id = Column(Integer, ForeignKey('table_object.id'))

    table_object_children_table_object = relationship("TableObject", foreign_keys=[table_object_id])
    table_object_children_child_table_object = relationship("TableObject", foreign_keys=[child_table_object_id])


class TableObjectChildrenFacilityRole(Base):
    __tablename__ = 'table_object_children_facility_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_role_id = Column(Integer, ForeignKey('facility_role.id'))
    table_object_children_id = Column(Integer, ForeignKey('table_object_children.id'))
    module_id = Column(Integer, ForeignKey('module.id'))

    table_object_children_facility_role_facility = relationship("FacilityRole", foreign_keys=[facility_role_id])
    table_object_children_facility_role_type = relationship("TableObjectChildren",
                                                            foreign_keys=[table_object_children_id])
    table_object_children_facility_role_module = relationship("Module", foreign_keys=[module_id])
    table_object_children_facility_role_unq = UniqueConstraint('facility_role_id', 'table_object_id')


class Field(Base):
    __tablename__ = 'field'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    field_name = Column(String(100))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    data_type_id = Column(Integer, ForeignKey('data_type.id'))
    unique = Column(Boolean)
    primary_key = Column(Boolean)
    length = Column(Integer)
    default = Column(String(255))
    foreign_key_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    foreign_key_field_id = Column(Integer, ForeignKey('field.id'))

    field_type = relationship("TableObject", foreign_keys=[table_object_id])
    field_data_type = relationship("DataType", foreign_keys=[data_type_id])
    field_foreign_key_table_object = relationship("TableObject", foreign_keys=[foreign_key_table_object_id])
    field_foreign_key_field = relationship("Field", foreign_keys=[foreign_key_field_id])


class FieldFacilityRole(Base):
    __tablename__ = 'field_facility_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_role_id = Column(Integer, ForeignKey('facility_role.id'))
    module_id = Column(Integer, ForeignKey('module.id'))
    field_id = Column(Integer, ForeignKey('field.id'))
    display_name = Column(String(100))
    visible = Column(Boolean)
    search_field = Column(Boolean)
    required = Column(Boolean)
    permission_id = Column(Integer, ForeignKey('permission.id'))

    field_facility_role_facility = relationship("FacilityRole", foreign_keys=[facility_role_id])
    field_facility_role_field = relationship("Field", foreign_keys=[field_id])
    field_facility_role_permission = relationship("Permission", foreign_keys=[permission_id])
    field_facility_role_unq = UniqueConstraint('facility_role_id', 'field_id', 'page_id')
    field_facility_role_module = relationship("Module", foreign_keys=[module_id])


class DataType(Base):
    __tablename__ = 'data_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)


class Permission(Base):
    __tablename__ = 'permission'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)


class Action(Base):
    __tablename__ = 'action'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    action_value = Column(String(255))


class NewUser(Base):
    __tablename__ = 'new_user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    first_name = Column(String(100))
    last_name = Column(String(100))
    password_hash = Column(String(100))
    email = Column(String(100))
    organization = Column(String(100))
    address1 = Column(String(100))
    address2 = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    postcode = Column(String(100))
    phone = Column(String(100))
    pi = Column(String(100))
    server = Column(String(100))
    directory = Column(String(100))


class TableQuery(Base):
    __tablename__ = 'table_query'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    display_name = Column(String(100))


class TableQueryRender(Base):
    __tablename__ = 'table_query_render'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    page_form_facility_role_id = Column(Integer, ForeignKey(
            'page_form_facility_role.id'))

    table_query_render_page_form_facility_role = relationship("PageFormFacilityRole",
                                                              foreign_keys=[page_form_facility_role_id])
    table_query_render_table_query = relationship("TableQuery", foreign_keys=[table_query_id])
    table_query_render_table_object = relationship("TableObject", foreign_keys=[table_object_id])


class TableQueryTableObject(Base):
    __tablename__ = 'table_query_table_object'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))

    table_query_type_type = relationship("TableObject", foreign_keys=[table_object_id])
    table_query_type_table_query = relationship("TableQuery", foreign_keys=[table_query_id])


class TableQueryField(Base):
    __tablename__ = 'table_query_field'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    field_id = Column(Integer, ForeignKey('field.id'))
    display_name = Column(String(100))

    table_query_field_field = relationship("Field", foreign_keys=[field_id])
    table_query_field_table_query = relationship("TableQuery", foreign_keys=[table_query_id])


class TableQueryCriteria(Base):
    __tablename__ = 'table_query_criteria'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    field_id = Column(Integer, ForeignKey('field.id'))
    value = Column(String(255))
    comparator = Column(String(10))

    table_query_criteria_table_query = relationship("TableQuery", foreign_keys=[table_query_id])
    table_query_criteria_field = relationship("Field", foreign_keys=[field_id])


class TableQueryOrder(Base):
    __tablename__ = 'table_query_order'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    field_id = Column(Integer, ForeignKey('field.id'))
    direction = Column(String(50))

    table_query_order_field = relationship("Field", foreign_keys=[field_id])
    table_query_order_table_query = relationship("TableQuery", foreign_keys=[table_query_id])


class Module(Base):
    __tablename__ = 'module'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    url_prefix = Column(String(50))


class ModuleFacilityRole(Base):
    __tablename__ = 'module_facility_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_role_id = Column(Integer, ForeignKey('facility_role.id'))
    module_id = Column(Integer, ForeignKey('module.id'))

    module_role_facility = relationship("FacilityRole", foreign_keys=[facility_role_id])
    module_facility_role_module = relationship("Module", foreign_keys=[module_id])




class UserRole( Base ):
    __tablename__ = 'user_role'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer, ForeignKey( 'organization.id' ) )
    order = Column( Integer )
    user_id = Column( Integer, ForeignKey( 'user.id' ) )
    role_id = Column(Integer)
    facility_role_id = Column( Integer, ForeignKey('facility_role.id' ))
    director = Column( Boolean )
    manager = Column( Boolean )

    user_role_user = relationship( "User", foreign_keys = [ user_id ] )
    user_role_facility_role = relationship( "FacilityRole", foreign_keys = [ facility_role_id ] )
    user_role_organization = relationship( "Organization", foreign_keys = [ organization_id ] )


class User( Base, UserMixin ):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer, ForeignKey( 'organization.id' ) )
    order = Column( Integer )
    password_hash = Column( String( 120 ) )
    password = Column( String( 120 ) )
    first_name = Column( String( 50 ) )
    last_name = Column( String( 50 ) )
    email = Column( String( 120 ), unique = True )
    address_id = Column( Integer, ForeignKey( 'address.id' ) )
    home_page = Column( String( 50 ) )
    current_user_role_id = Column( Integer, ForeignKey( 'user_role.id' ) )
    user_user_role = relationship( "UserRole", foreign_keys = [ current_user_role_id ] )
    user_organization = relationship( "Organization", foreign_keys = [ organization_id ] )
    roles = relationship('FacilityRole', secondary='user_role',primaryjoin='user_role.c.user_id == User.id',
        secondaryjoin='user_role.c.facility_role_id == FacilityRole.id',
        backref=backref('users', lazy='dynamic'))

    def get_id(self):
        return str( self.id )

    def set_password( self, password ):
        self.password_hash = generate_password_hash( password )

    def verify_password( self, password ):
        return check_password_hash( self.password_hash, password )

    @staticmethod
    def get_password_hash( password ):
        return generate_password_hash( password )

    def get_role( self ):
        return ROLE[ self.role_id ]

    def __repr__( self ):
        return '<User %r>' % ( self.name )

class UserOrganization( Base ):
    __tablename__ = 'user_organization'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    user_id = Column( Integer, ForeignKey( 'user.id' ) )
    user_organization_id = Column( Integer, ForeignKey( 'organization.id' ) )
    default_organization = Column( Boolean )

    user_organization_organization = relationship( 'Organization', foreign_keys = [ user_organization_id ] )
    user_organization_user = relationship( 'User', foreign_keys = [ user_id ] )

class Organization( Base ):
    __tablename__ = 'organization'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    address_id = Column( Integer, ForeignKey( 'address.id' ) )
    billing_address_id = Column( Integer )
    organization_type_id = Column( Integer )
    parent_id = Column( Integer, ForeignKey( 'organization.id' ) )

    parent = relation( 'Organization', remote_side = [ id ] )

class OrganizationType( Base ):
    __tablename__ = 'organization_type'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )

@lm.user_loader
def load_user( id ):
    return User.query.get( int( id ) )
