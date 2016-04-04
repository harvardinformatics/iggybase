from iggybase.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship, relation, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.security import UserMixin, RoleMixin
from iggybase.admin.constants import ROLE
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
    root_organization_id = Column(Integer)


class Level(Base):
    __tablename__ = 'level'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)


class Role(Base, RoleMixin):
    ''' Role will be a combination of Facility and Level,
        a user may belong to more than one Facility but at different functional
        levels (admin, user, etc).
        Role will determine what functionality on the site the user has access
        to.
    '''
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_id = Column(Integer, ForeignKey('facility.id'))
    level_id = Column(Integer, ForeignKey('level.id'))

    role_facility = relationship("Facility", foreign_keys=[facility_id])
    role_level = relationship("Level", foreign_keys=[level_id])
    role_unq = UniqueConstraint('facility_id', 'level_id')

    def __repr__(self):
        return "<Role=%s, description=%s, id=%d, level=%s, facility=%s>)" % \
               (self.name, self.description, self.id,
                self.role_level.name, self.role_facility.name)


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
    module_id = Column(Integer, ForeignKey('module.id'))
    url_path = Column(String(512), unique=True)
    url_params = Column(String(1024))  ## Stored as JSON

    parent = relationship('Menu', remote_side=[id])
    children = relationship('Menu')
    menu_menu_type = relationship("MenuType", foreign_keys=[menu_type_id])
    menu_module = relationship("Module", foreign_keys=[module_id])

    def __repr__(self):
        return "<Menu(name=%s, description=%s, id=%d)>" % \
               (self.name, self.description, self.id)


class MenuRole(Base):
    __tablename__ = 'menu_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    role_id = Column(Integer, ForeignKey('role.id'))
    menu_id = Column(Integer, ForeignKey('menu.id'))
    menu_class = Column(String(100))

    menu_role_role = relationship(
            "Role", foreign_keys=[role_id])
    menu_role_unq = UniqueConstraint('role_id', 'menu_id')
    menu_role_menu = relationship("Menu", foreign_keys=[menu_id])

    def __repr__(self):
        return "<MenuRole(name=%s, description=%s, id=%d, menu_id=%d, order=%d>)" % \
               (self.name, self.description, self.id, self.menu_id, self.order)

class Route(Base):
    __tablename__ = 'route'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    module_id = Column(Integer, ForeignKey('module.id'))
    url_path = Column(String(512), unique=True)

    route_module = relationship("Module", foreign_keys=[module_id])

    def __repr__(self):
        return "<Route(name=%s, description=%s, id=%d)>" % \
               (self.name, self.description, self.id)

class MenuNew(Base):
    __tablename__ = 'menu_new'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('menu_new.id'))
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    menu_type_id = Column(Integer, ForeignKey('menu_type.id'))
    route_id = Column(Integer, ForeignKey('route.id'))
    url_params = Column(String(1024))  ## Stored as JSON
    dynamic_suffix = Column(String(255))
    display_name = Column(String(50))

    parent = relationship('MenuNew', remote_side=[id])
    children = relationship('MenuNew')
    menu_new_menu_type = relationship("MenuType", foreign_keys=[menu_type_id])
    menu_new_route = relationship("Route", foreign_keys=[route_id])

    def __repr__(self):
        return "<MenuNew(name=%s, description=%s, id=%d)>" % \
               (self.name, self.description, self.id)

class RouteRole(Base):
    __tablename__ = 'route_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    role_id = Column(Integer, ForeignKey('role.id'))
    route_id = Column(Integer, ForeignKey('route.id'))

    route_role_role = relationship(
            "Role", foreign_keys=[role_id])
    route_role_unq = UniqueConstraint('role_id', 'route_id')
    route_role_route = relationship("Route", foreign_keys=[route_id])

    def __repr__(self):
        return "<RouteRole(name=%s, description=%s, id=%d, route_id=%d, order=%d>)" % \
               (self.name, self.description, self.id, self.route_id, self.order)



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


class PageFormJavascript(Base):
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


class PageFormRole(Base):
    __tablename__ = 'page_form_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    role_id = Column(Integer, ForeignKey('role.id'))
    page_form_id = Column(Integer, ForeignKey('page_form.id'))

    page_role_role = relationship("Role", foreign_keys=[role_id])
    page_role_page = relationship("PageForm", foreign_keys=[page_form_id])


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
    submit_action_url = Column(String(255))

    page_form_button_page_form = relationship("PageForm", foreign_keys=[page_form_id])


class PageFormButtonRole(Base):
    __tablename__ = 'page_form_button_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    role_id = Column(Integer, ForeignKey('role.id'))
    page_form_button_id = Column(Integer, ForeignKey('page_form_button.id'))

    page_form_button_role_role = relationship("Role", foreign_keys=[role_id])
    page_form_button_role_page_form = relationship("PageFormButton", foreign_keys=[page_form_button_id])


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
    admin_table = Column(Boolean)
    new_name_prefix = Column(String(10))
    new_name_id = Column(Integer)
    id_length = Column(Integer)

    def get_new_name(self):
        new_name = self.new_name_prefix + str(self.new_name_id).zfill(self.id_length)
        self.new_name_id += 1
        return new_name


class TableObjectRole(Base):
    __tablename__ = 'table_object_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    role_id = Column(Integer, ForeignKey('role.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    display_name = Column(String(100))

    table_object_role_role = relationship("Role", foreign_keys=[role_id])
    table_object_role_table_object = relationship("TableObject", foreign_keys=[table_object_id])
    table_object_role_unq = UniqueConstraint('role_id', 'table_object_id')


class TableObjectMany(Base):
    __tablename__ = 'table_object_many'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    first_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    link_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    second_table_object_id = Column(Integer, ForeignKey('table_object.id'))

    table_object_many_first_table_object = relationship("TableObject", foreign_keys=[first_table_object_id])
    table_object_many_second_table_object = relationship("TableObject", foreign_keys=[link_table_object_id])
    table_object_many_link_table_object = relationship("TableObject", foreign_keys=[second_table_object_id])


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
    child_link_field_id = Column(Integer, ForeignKey('field.id'))

    table_object_children_table_object = relationship("TableObject", foreign_keys=[table_object_id])
    table_object_children_child_table_object = relationship("TableObject", foreign_keys=[child_table_object_id])
    table_object_children_field = relationship("Field", foreign_keys=[child_link_field_id])


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
    field_class = Column(String(100))
    foreign_key_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    foreign_key_field_id = Column(Integer, ForeignKey('field.id'))
    foreign_key_display = Column(Integer, ForeignKey('field.id'))

    field_type = relationship("TableObject", foreign_keys=[table_object_id])
    field_data_type = relationship("DataType", foreign_keys=[data_type_id])
    field_foreign_key_table_object = relationship("TableObject", foreign_keys=[foreign_key_table_object_id])
    field_foreign_key_field = relationship("Field", foreign_keys=[foreign_key_field_id])
    field_foreign_key_display = relationship("Field", foreign_keys=[foreign_key_display])


class FieldRole(Base):
    __tablename__ = 'field_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    role_id = Column(Integer, ForeignKey('role.id'))
    field_id = Column(Integer, ForeignKey('field.id'))
    display_name = Column(String(100))
    visible = Column(Boolean)
    search_field = Column(Boolean)
    required = Column(Boolean)
    permission_id = Column(Integer, ForeignKey('permission.id'))

    field_role_role = relationship("Role", foreign_keys=[role_id])
    field_role_field = relationship("Field", foreign_keys=[field_id])
    field_role_permission = relationship("Permission", foreign_keys=[permission_id])
    field_role_unq = UniqueConstraint('role_id', 'field_id', 'page_id')


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
    """This table initially works for database changes create and update and as a result,
    sends an email to a list of recipients. It will change however as more action types
    are introduced.
    """
    __tablename__ = 'action'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    order = Column(Integer)
    action_type = Column(String(50)) #['email'|'workflow'|'cron']
    email_text = Column(String(1024))
    email_recipients = Column(String(1024)) # csv email@addresses
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    field_id = Column(Integer, ForeignKey('field_id'))
    field_value = Column(String(255))  # eg. 'Turnbaugh' | 'Purchase_Order'
    action_value = Column(String(255)) # ['new'|'dirty'|deleted']

    table_object = relationship("TableObject")
    organization = relationship("Organization")

    def __repr__(self):
        return "<Action(name=%s, id=%s, active=%s, organization=%s, table_object=%s" \
            (self.name, repr(self.active), self.organization.name,
             self.table_object.name)


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
    page_form_role_id = Column(Integer, ForeignKey(
            'page_form_role.id'))

    table_query_render_page_form_role = relationship("PageFormRole",
                                                              foreign_keys=[page_form_role_id])
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
    visible = Column(Boolean)

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

class TableQueryCalculation(Base):
    __tablename__ = 'table_query_calculation'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    function = Column(String(100))
    table_query_field_id = Column(Integer, ForeignKey('table_query_field.id'))

    table_query_calculation_table_query_field = relationship("TableQueryField", foreign_keys=[table_query_field_id])

class TableQueryCalculationField(Base):
    __tablename__ = 'table_query_calculation_field'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    table_query_calculation_id = Column(Integer,
            ForeignKey('table_query_calculation.id'))
    table_query_field_id = Column(Integer, ForeignKey('table_query_field.id'))

    table_query_calculation_field_table_query_calculation = relationship("TableQueryCalculation", foreign_keys=[table_query_calculation_id])
    table_query_calculation_field_table_query_field = relationship("TableQueryField", foreign_keys=[table_query_field_id])

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
    blueprint = Column(Boolean)


class ModuleFacility(Base):
    __tablename__ = 'module_facility'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    facility_id = Column(Integer, ForeignKey('facility.id'))
    module_id = Column(Integer, ForeignKey('module.id'))

    module_facility_facility = relationship("Facility", foreign_keys=[facility_id])
    module_facility_module = relationship("Module", foreign_keys=[module_id])


class UserRole(Base):
    __tablename__ = 'user_role'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    order = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    role_id = Column(Integer, ForeignKey('role.id'))
    director = Column(Boolean)
    manager = Column(Boolean)

    user_role_user = relationship("User", foreign_keys=[user_id])
    user_role_role = relationship("Role", foreign_keys=[role_id])
    user_role_organization = relationship("Organization", foreign_keys=[organization_id])


class User(Base, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    order = Column(Integer)
    password_hash = Column(String(120))
    password = Column(String(120))
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(120), unique=True)
    address_id = Column(Integer, ForeignKey('address.id'))
    home_page = Column(String(50))
    current_user_role_id = Column(Integer, ForeignKey('user_role.id'))

    user_user_role = relationship("UserRole", foreign_keys=[current_user_role_id])
    user_organization = relationship("Organization", foreign_keys=[organization_id])
    roles = relationship('Role', secondary='user_role', primaryjoin='user_role.c.user_id == User.id',
                         secondaryjoin='user_role.c.role_id == Role.id', order_by='Role.name',
                         backref=backref('users', lazy='dynamic'))

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_password_hash(password):
        return generate_password_hash(password)

    def get_role(self):
        return ROLE[self.role_id]

    def __repr__(self):
        return '<User %r>' % (self.name)


class UserOrganization(Base):
    __tablename__ = 'user_organization'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    user_organization_id = Column(Integer, ForeignKey('organization.id'))
    default_organization = Column(Boolean)

    user_organization_organization = relationship('Organization', foreign_keys=[user_organization_id])
    user_organization_user = relationship('User', foreign_keys=[user_id])

class Institution(Base):
    __tablename__ = 'institution'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)


class Department(Base):
    __tablename__ = 'department'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    institution_id = Column(Integer, ForeignKey('institution.id'))

    department_institution = relationship("Institution",
            foreign_keys=[institution_id])


class Organization(Base):
    __tablename__ = 'organization'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)
    address_id = Column(Integer)
    billing_address_id = Column(Integer)
    organization_type_id = Column(Integer)
    parent_id = Column(Integer, ForeignKey('organization.id'))
    department_id = Column(Integer, ForeignKey('department.id'))

    parent = relation('Organization', remote_side=[id])
    organization_department = relationship("Department",
            foreign_keys=[department_id])


class OrganizationType(Base):
    __tablename__ = 'organization_type'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean)
    organization_id = Column(Integer)
    order = Column(Integer)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
