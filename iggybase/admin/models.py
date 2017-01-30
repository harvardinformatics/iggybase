from iggybase.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, relation, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.security import UserMixin, RoleMixin
from iggybase.admin.constants import ROLE
from iggybase.extensions import lm
import random


class Institution(Base):
    table_type = 'admin'

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class Department(Base):
    table_type = 'admin'
    institution_id = Column(Integer, ForeignKey('institution.id'))

    department_institution = relationship("Institution", foreign_keys=[institution_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class OrganizationType(Base):
    table_type = 'admin'

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)

class Address(Base):
    table_type = 'admin'

    address_1 = Column(String(255))
    address_2 = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    postcode = Column(String(255))
    country = Column(String(255))

class Organization(Base):
    table_type = 'admin'

    address_id = Column(Integer, ForeignKey('address.id'))
    billing_address_id = Column(Integer)
    organization_type_id = Column(Integer, ForeignKey('organization_type.id'))
    parent_id = Column(Integer, ForeignKey('organization.id'))
    # organizations must have an institution but can also have a dept
    # dept is most applicable to universities and less so to industry
    department_id = Column(Integer, ForeignKey('department.id'))
    institution_id = Column(Integer, ForeignKey('institution.id'))

    parent = relation('Organization', remote_side="Organization.id", foreign_keys=[parent_id])
    organization_department = relationship("Department", foreign_keys=[department_id])
    organization_organization_type = relationship("OrganizationType", foreign_keys=[organization_type_id])
    organization_address = relationship("Address", foreign_keys=[address_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id)


class TableObject(Base):
    table_type = 'admin'
    admin_table = Column(Boolean)
    new_name_prefix = Column(String(10))
    new_name_id = Column(Integer)
    id_length = Column(Integer)
    display_name = Column(String(100))
    extends_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    note_enabled = Column(Boolean)

    table_object_extends_table_object = relationship("TableObject", foreign_keys=[extends_table_object_id])

    def get_new_name(self):
        if self.new_name_prefix is not None and self.new_name_prefix != "" and self.new_name_id is not None and \
                self.id_length is not None:
            new_name = self.new_name_prefix + str(self.new_name_id).zfill(self.id_length)
            self.new_name_id += 1
        else:
            new_name = self.name + str(random.randint(1000000000, 9999999999))

        return new_name

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class Field(Base):
    table_type = 'admin'
    display_name = Column(String(100))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    data_type_id = Column(Integer, ForeignKey('data_type.id'))
    unique = Column(Boolean)
    primary_key = Column(Boolean)
    length = Column(Integer)
    default = Column(String(255))
    field_class = Column(String(100))
    select_list_id = Column(Integer, ForeignKey('select_list.id'))
    foreign_key_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    foreign_key_field_id = Column(Integer, ForeignKey('field.id'))
    foreign_key_display = Column(Integer, ForeignKey('field.id'))
    drop_down_list_limit = Column(Integer)
    dynamic_field_definition_field_id  = Column(Integer, ForeignKey('field.id'))

    field_type = relationship("TableObject", foreign_keys=[table_object_id])
    field_data_type = relationship("DataType", foreign_keys=[data_type_id])
    field_select_list = relationship("SelectList", foreign_keys=[select_list_id])
    field_foreign_key_table_object = relationship("TableObject", foreign_keys=[foreign_key_table_object_id])
    field_foreign_key_field = relationship("Field", foreign_keys=[foreign_key_field_id])
    field_foreign_key_display = relationship("Field", foreign_keys=[foreign_key_display])
    field_dynamic_field_definition_field = relationship("Field", foreign_keys=[dynamic_field_definition_field_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class DataType(Base):
    table_type = 'admin'
    db_data_type = Column(String(50))

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class Level(Base):
    __tablename__ = 'level'
    table_type = 'admin'

    def __repr__(self):
        return "<%s(class=%s, name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__, self.name, self.description, self.id, self.organization_id,
                getattr(self, 'order', None))


class Role(Base, RoleMixin):
    ''' Role will be a combination of Facility and Level,
        a user may belong to more than one Facility but at different functional
        levels (admin, user, etc).
        Role will determine what functionality on the site the user has access
        to.
    '''
    table_type = 'admin'
    facility_id = Column(Integer, ForeignKey('facility.id'))
    level_id = Column(Integer, ForeignKey('level.id'))
    default_home = Column(String(100))

    role_facility = relationship("Facility", foreign_keys=[facility_id])
    role_level = relationship("Level", foreign_keys=[level_id])
    role_unq = UniqueConstraint('facility_id', 'level_id')

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class Facility(Base):
    table_type = 'admin'
    root_organization_id = Column(Integer)
    banner_img = Column(String(255))
    banner_title = Column(String(255))
    banner_subtitle = Column(String(255))
    css = Column(String(255))
    table_suffix = Column(String(255))

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class MenuRole(Base):
    table_type = 'admin'
    role_id = Column(Integer, ForeignKey('role.id'))
    menu_id = Column(Integer, ForeignKey('menu.id'))
    menu_class = Column(String(100))
    display_name = Column(String(50))

    menu_role_role = relationship(
        "Role", foreign_keys=[role_id])
    menu_role_unq = UniqueConstraint('role_id', 'menu_id')
    menu_role_menu = relationship("Menu", foreign_keys=[menu_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class Route(Base):
    table_type = 'admin'
    module_id = Column(Integer, ForeignKey('module.id'))
    url_path = Column(String(512), unique=True)
    display_name = Column(String(50))

    route_module = relationship("Module", foreign_keys=[module_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class Menu(Base):
    table_type = 'admin'
    parent_id = Column(Integer, ForeignKey('menu.id'))
    menu_type_id = Column(Integer, ForeignKey('menu_type.id'))
    route_id = Column(Integer, ForeignKey('route.id'))
    url_params = Column(String(1024))  ## Stored as JSON
    dynamic_suffix = Column(String(255))
    display_name = Column(String(50))

    parent = relationship('Menu', remote_side='Menu.id')
    children = relationship('Menu')
    menu_new_menu_type = relationship("MenuType", foreign_keys=[menu_type_id])
    menu_new_route = relationship("Route", foreign_keys=[route_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class RouteRole(Base):
    table_type = 'admin'
    role_id = Column(Integer, ForeignKey('role.id'))
    route_id = Column(Integer, ForeignKey('route.id'))

    route_role_role = relationship(
        "Role", foreign_keys=[role_id])
    route_role_unq = UniqueConstraint('role_id', 'route_id')
    route_role_route = relationship("Route", foreign_keys=[route_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class MenuType(Base):
    table_type = 'admin'

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class SelectList(Base):
    table_type = 'admin'

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class SelectListItem(Base):
    table_type = 'admin'
    select_list_id = Column(Integer, ForeignKey('select_list.id'))
    display_name = Column(String(50))

    select_list_item_select_list = relationship("SelectList", foreign_keys=[select_list_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class PageForm(Base):
    table_type = 'admin'
    page_title = Column(String(50))
    page_header = Column(String(50))
    page_template = Column(String(100))
    parent_id = Column(Integer, ForeignKey('page_form.id'))

    parent = relation('PageForm', remote_side="PageForm.id", foreign_keys=[parent_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class PageFormJavascript(Base):
    table_type = 'admin'
    page_form_id = Column(Integer, ForeignKey('page_form.id'))
    page_javascript = Column(String(100))

    page_javascript_page = relationship("PageForm", foreign_keys=[page_form_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class PageFormContext(Base):
    table_type = 'admin'

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class PageFormButton(Base):
    table_type = 'admin'
    button_type = Column(String(100))
    button_class = Column(String(100))
    button_value = Column(String(100))
    button_id = Column(String(100))
    special_props = Column(String(255))
    submit_action_url = Column(String(255))
    display_name = Column(String(100))

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class PageFormButtonRole(Base):
    table_type = 'admin'
    role_id = Column(Integer, ForeignKey('role.id'))
    page_form_button_id = Column(Integer, ForeignKey('page_form_button.id'))
    display_name = Column(String(50))

    page_form_button_role_role = relationship("Role", foreign_keys=[role_id])
    page_form_button_role_page_form = relationship("PageFormButton", foreign_keys=[page_form_button_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class PageFormButtonContext(Base):
    table_type = 'admin'
    page_form_id = Column(Integer, ForeignKey('page_form.id'))
    page_form_button_id = Column(Integer, ForeignKey('page_form_button.id'))
    page_form_context_id = Column(Integer, ForeignKey('page_form_context.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    button_location_id = Column(Integer, ForeignKey('select_list_item.id'))

    page_form_button_context_select_list_item = relationship("SelectListItem", foreign_keys=[button_location_id])
    page_form_button_context_page_form = relationship("PageForm", foreign_keys=[page_form_id])
    page_form_button_context_page_form_button = relationship("PageFormButton", foreign_keys=[page_form_button_id])
    page_form_button_context_page_form_context = relationship("PageFormContext", foreign_keys=[page_form_context_id])
    page_form_button_context_table_object = relationship("TableObject", foreign_keys=[table_object_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class TableObjectRole(Base):
    table_type = 'admin'
    role_id = Column(Integer, ForeignKey('role.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    display_name = Column(String(100))

    table_object_role_role = relationship("Role", foreign_keys=[role_id])
    table_object_role_table_object = relationship("TableObject", foreign_keys=[table_object_id])
    table_object_role_unq = UniqueConstraint('role_id', 'table_object_id')

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class TableObjectMany(Base):
    table_type = 'admin'
    first_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    link_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    second_table_object_id = Column(Integer, ForeignKey('table_object.id'))

    table_object_many_first_table_object = relationship("TableObject", foreign_keys=[first_table_object_id])
    table_object_many_second_table_object = relationship("TableObject", foreign_keys=[link_table_object_id])
    table_object_many_link_table_object = relationship("TableObject", foreign_keys=[second_table_object_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class TableObjectChildren(Base):
    table_type = 'admin'
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    child_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    child_link_field_id = Column(Integer, ForeignKey('field.id'))

    table_object_children_table_object = relationship("TableObject", foreign_keys=[table_object_id])
    table_object_children_child_table_object = relationship("TableObject", foreign_keys=[child_table_object_id])
    table_object_children_field = relationship("Field", foreign_keys=[child_link_field_id])


class TableObjectDynamicLink(Base):
    table_type = 'admin'
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    dynamic_table_object_id = Column(Integer, ForeignKey('table_object.id'))
    dynamic_field_id = Column(Integer, ForeignKey('field.id'))

    table_object_dynamic_table_object = relationship("TableObject", foreign_keys=[table_object_id])
    table_object_dynamic_child_table_object = relationship("TableObject", foreign_keys=[dynamic_table_object_id])
    table_object_dynamic_field = relationship("Field", foreign_keys=[dynamic_field_id])


class FieldRole(Base):
    __tablename__ = 'field_role'
    table_type = 'admin'
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


class Permission(Base):
    __tablename__ = 'permission'
    table_type = 'admin'

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)




class TableQuery(Base):
    table_type = 'admin'
    display_name = Column(String(100))

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)

class TableQueryRender(Base):
    table_type = 'admin'
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    dynamic_field = Column(String(100))
    route_role_id = Column(Integer, ForeignKey(
        'route_role.id'))

    table_query_render_route_role = relationship("RouteRole",
                                                     foreign_keys=[route_role_id])
    table_query_render_table_query = relationship("TableQuery", foreign_keys=[table_query_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class TableQueryTableObject(Base):
    table_type = 'admin'
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))

    table_query_type_type = relationship("TableObject", foreign_keys=[table_object_id])
    table_query_type_table_query = relationship("TableQuery", foreign_keys=[table_query_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class TableQueryField(Base):
    table_type = 'admin'
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    field_id = Column(Integer, ForeignKey('field.id'))
    display_name = Column(String(100))
    visible = Column(Boolean)
    group_func = Column(String(50))
    group_by = Column(Boolean)
    order_by = Column(Integer)

    table_query_field_field = relationship("Field", foreign_keys=[field_id])
    table_query_field_table_query = relationship("TableQuery", foreign_keys=[table_query_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class TableQueryCriteria(Base):
    table_type = 'admin'
    table_query_id = Column(Integer, ForeignKey('table_query.id'))
    field_id = Column(Integer, ForeignKey('field.id'))
    value = Column(String(255))
    comparator = Column(String(10))

    table_query_criteria_table_query = relationship("TableQuery", foreign_keys=[table_query_id])
    table_query_criteria_field = relationship("Field", foreign_keys=[field_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class TableQueryCalculation(Base):
    table_type = 'admin'
    function = Column(String(100))
    table_query_field_id = Column(Integer, ForeignKey('table_query_field.id'))

    table_query_calculation_table_query_field = relationship("TableQueryField", foreign_keys=[table_query_field_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class TableQueryCalculationField(Base):
    table_type = 'admin'
    table_query_calculation_id = Column(Integer,
                                        ForeignKey('table_query_calculation.id'))
    table_query_field_id = Column(Integer, ForeignKey('table_query_field.id'))

    table_query_calculation_field_table_query_calculation = relationship("TableQueryCalculation",
                                                                         foreign_keys=[table_query_calculation_id])
    table_query_calculation_field_table_query_field = relationship("TableQueryField",
                                                                   foreign_keys=[table_query_field_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class Workflow(Base):
    table_type = 'admin'
    display_name = Column(String(100))
    notes = Column(String(255))

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)

class WorkflowRole(Base):
    table_type = 'admin'
    display_name = Column(String(100))
    role_id = Column(Integer, ForeignKey('role.id'))
    workflow_id = Column(Integer, ForeignKey('workflow.id'))

    workflow_role_role = relationship("Role", foreign_keys=[role_id])
    workflow_role_workflow = relationship("Workflow", foreign_keys=[workflow_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)

class Step(Base):
    table_type = 'admin'
    display_name = Column(String(100))
    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    route_id = Column(Integer, ForeignKey('route.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    params = Column(String(255))
    notes = Column(String(255))
    dynamic_field = Column(Integer, ForeignKey('field.id'))

    step_workflow = relationship("Workflow", foreign_keys=[workflow_id])
    step_route = relationship("Route", foreign_keys=[route_id])
    step_table_object = relationship("TableObject", foreign_keys=[table_object_id])
    step_dynamic_field = relationship("Field", foreign_keys=[dynamic_field])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)

class WorkItemGroup(Base):
    table_type = 'admin'
    display_name = Column(String(100))
    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    step_id = Column(Integer, ForeignKey('step.id'))
    assigned_to = Column(Integer, ForeignKey('user.id'))
    notes = Column(String(255))
    status = Column(Integer, ForeignKey('select_list.id'))
    before_action_complete = Column(Boolean)

    work_item_group_workflow = relationship("Workflow", foreign_keys=[workflow_id])
    work_item_group_step = relationship("Step", foreign_keys=[step_id])
    work_item_group_user = relationship("User", foreign_keys=[assigned_to])
    work_item_group_status = relationship("SelectList", foreign_keys=[status])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id)

class WorkItem(Base):
    table_type = 'admin'
    work_item_group_id = Column(Integer, ForeignKey('work_item_group.id'))
    table_object_id = Column(Integer, ForeignKey('table_object.id'))
    row_id = Column(Integer)
    notes = Column(String(255))
    parent_id = Column(Integer, ForeignKey('work_item.id'))


    work_item_work_item_group = relationship("WorkItemGroup", foreign_keys=[work_item_group_id])
    work_item_table_object = relationship("TableObject", foreign_keys=[table_object_id])
    work_item_work_item = relation('WorkItem', remote_side="WorkItem.id", foreign_keys=[parent_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)

class Module(Base):
    table_type = 'admin'
    url_prefix = Column(String(50))
    blueprint = Column(Boolean)

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id)


class ModuleFacility(Base):
    table_type = 'admin'
    facility_id = Column(Integer, ForeignKey('facility.id'))
    module_id = Column(Integer, ForeignKey('module.id'))

    module_facility_facility = relationship("Facility", foreign_keys=[facility_id])
    module_facility_module = relationship("Module", foreign_keys=[module_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d, order=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id, self.order)


class UserRole(Base):
    table_type = 'admin'
    user_id = Column(Integer, ForeignKey('user.id'))
    role_id = Column(Integer, ForeignKey('role.id'))
    director = Column(Boolean)
    manager = Column(Boolean)

    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role", foreign_keys=[role_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id)


class User(Base, UserMixin):
    table_type = 'admin'
    password_hash = Column(String(120))
    password = Column(String(120))
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(120), unique=True)
    address_id = Column(Integer, ForeignKey('address.id'))
    home_page = Column(String(50))
    current_user_role_id = Column(Integer, ForeignKey('user_role.id'))

    user_user_role = relationship("UserRole", foreign_keys=[current_user_role_id])
    user_roles = relationship('UserRole', primaryjoin='user_role.c.user_id == User.id',
                              backref=backref('users'))
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

class Position(Base):
    __tablename__ = 'position'
    table_type = 'admin'


class UserOrganization(Base):
    table_type = 'admin'
    user_id = Column(Integer, ForeignKey('user.id'))
    user_organization_id = Column(Integer, ForeignKey('organization.id'))
    default_organization = Column(Boolean)

    user_organization_organization = relationship('Organization', foreign_keys=[user_organization_id])
    user_organization_user = relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return "<%s(name=%s, description=%s, id=%d, organization_id=%d)>" % \
               (self.__class__.__name__, self.name, self.description, self.id, self.organization_id)

class UserOrganizationPosition(Base):
    table_type = 'admin'
    user_id = Column(Integer, ForeignKey('user.id'))
    position_id = Column(Integer, ForeignKey('position.id'))

    user_organization_position_user_organization = relationship('User', foreign_keys=[user_id])
    user_organization_position_position = relationship('Position', foreign_keys=[position_id])


class Action(Base):
    """Actions taken for a specific event. Events can have multiple actions
    This is a base class.
    """
    table_type = 'admin'
    namespace = Column(String(255), default=None)
    function = Column(String(255), default=None)
    params = Column(String(255), default=None)
    type = Column(String(50), default=None)


class ActionStep(Base):
    table_type = 'admin'
    action_id = Column(Integer, ForeignKey('action.id'), default=None)
    step_id = Column(Integer, ForeignKey('step.id'), default=None)
    timing = Column(Integer, ForeignKey('select_list_item.id'), default=None)

    action_step_timing = relationship("SelectListItem", foreign_keys=[timing])
    action_step_step = relationship('Step', foreign_keys=[step_id])
    action_step_action = relationship("Action", foreign_keys=[action_id])


class ActionTableObject(Base):
    table_type = 'admin'
    action_id = Column(Integer, ForeignKey('action.id'), default=None)
    table_object_id = Column(Integer, ForeignKey('table_object.id'), default=None)
    event_id = Column(Integer, ForeignKey('select_list_item.id'), default=None)
    field_id = Column(Integer, ForeignKey('field.id'), default=None)
    field_value = Column(String(255), default=None)

    action_function_call_timing = relationship("SelectListItem", foreign_keys=[event_id])
    action_table_object_table_object = relationship('TableObject', foreign_keys=[table_object_id])
    action_table_object_action = relationship("Action", foreign_keys=[action_id])
    action_table_object_field = relationship('Field', foreign_keys=[field_id])


class ActionEmail(Action):
    table_type = 'admin'
    id = Column(Integer, ForeignKey('action.id'), primary_key=True)
    text = Column(Integer, default=None)
    subject = Column(String(255), default=None)
    recipients = Column(Integer, default=None)
    cc = Column(Integer, default=None)
    bcc = Column(Integer, default=None)
    attachment = Column(String(255), default=None)

    action_email_action = relationship("Action", foreign_keys=[id])

    __mapper_args__ = {'polymorphic_identity': 'action_email'}


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
