from iggybase.database import StaticBase
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
import datetime

class Facility( StaticBase ):
    __tablename__ = 'facility'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )

class Role( StaticBase ):
    __tablename__ = 'role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )

class FacilityRole( StaticBase ):
    __tablename__ = 'facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_id = Column( Integer, ForeignKey( 'facility.id' ) )
    role_id = Column( Integer, ForeignKey( 'role.id' ) )

    facility_role_facility = relationship( "Facility", foreign_keys = [ facility_id ] )
    facility_role_role = relationship( "Role", foreign_keys = [ role_id ] )
    facility_role_unq = UniqueConstraint( 'facility_id', 'role_id' )

    def __repr__(self):
        return "<FacilityRole=%s, description=%s, id=%d, role=%s, facility=%s>)" % \
            (self.name, self.description, self.id,
             self.facility_role_role.name, self.facility_role_facility.name)


class Menu( StaticBase ):
    __tablename__ = 'menu'
    id = Column( Integer, primary_key = True )
    parent_id = Column(Integer, ForeignKey('menu.id'))
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    menu_type_id = Column( Integer, ForeignKey( 'menu_type.id' ) )
    menu_url_id = Column(Integer, ForeignKey('menu_url.id'))

    parent = relationship('Menu', remote_side=[id])
    children = relationship('Menu')
    menu_type = relationship( "MenuType", foreign_keys = [ menu_type_id ] )
    menu_url = relationship("MenuUrl", backref='menu')
    facility_role = relationship('MenuFacilityRole', uselist=False, back_populates='menu')

    def __repr__(self):
        return "<Menu(name=%s, description=%s, id=%d)>" % \
            (self.name, self.description, self.id)



class MenuFacilityRole( StaticBase ):
    __tablename__ = 'menu_facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_role_id = Column( Integer, ForeignKey( 'facility_role.id' ) )
    menu_id = Column( Integer, ForeignKey( 'menu.id' ) )

    menu_facility_role_facility = relationship(
        "FacilityRole", foreign_keys = [ facility_role_id ] )
    menu = relationship( "Menu", back_populates='facility_role' )
    menu_facility_role_unq = UniqueConstraint( 'facility_role_id', 'menu_id' )

    def __repr__(self):
        return "<MenuFacilityRole(name=%s, description=%s, id=%d, menu_id=%d, order=%d>)" % \
            (self.name, self.description, self.id, self.menu_id, self.order)




class MenuType( StaticBase ):
    __tablename__ = 'menu_type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

    def __repr__(self):
        return "<MenuType(name=%s, description=%s, id=%d>)" % \
            (self.name, self.description, self.id)


class MenuUrl( StaticBase ):
    """Matches a url to a menu. One to many relationship with Menu.
    """
    __tablename__ = 'menu_url'
    id = Column(Integer, primary_key=True)

    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

    url_path = Column(String(512), unique=True)
    url_params = Column(String(1024)) ## Stored as JSON

    def __repr__(self):
        return "<MenuUrl(name=%s, description=%s, id=%d, url_path=%s>)" % \
            (self.name, self.description, self.id, self.url_path)


class MenuItem( StaticBase ):
    __tablename__ = 'menu_item'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ) )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    menu_item_value = Column( String( 250 ) )
    menu_id = Column( Integer, ForeignKey( 'menu.id' ) )

    menu_item_menu = relationship( "Menu", foreign_keys = [ menu_id ] )

class MenuItemFacilityRole( StaticBase ):
    __tablename__ = 'menu_item_facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_role_id = Column( Integer, ForeignKey( 'facility_role.id' ) )
    menu_item_id = Column( Integer, ForeignKey( 'menu_item.id' ) )

    menu_item_facility_role_facility = relationship( "FacilityRole", foreign_keys = [ facility_role_id ] )
    menu_item_facility_role_menu_item = relationship( "MenuItem", foreign_keys = [ menu_item_id ] )
    menu_item_facility_role_unq = UniqueConstraint( 'facility_role_id', 'menu_item_id' )

class PageForm( StaticBase ):
    __tablename__ = 'page_form'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    page_title = Column( String( 50 ) )
    page_header = Column( String( 50 ) )
    page_template = Column( String( 100 ) )

class PageFormJavaScript( StaticBase ):
    __tablename__ = 'page_form_javascript'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    page_form_id = Column( Integer, ForeignKey( 'page_form.id' ) )
    page_javascript = Column( String( 100 ) )

    page_javascript_page = relationship( "PageForm", foreign_keys = [ page_form_id ] )

class PageFormFacilityRole( StaticBase ):
    __tablename__ = 'page_form_facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_role_id = Column( Integer, ForeignKey( 'facility_role.id' ) )
    page_form_id = Column( Integer, ForeignKey( 'page_form.id' ) )

    page_facility_role_facility = relationship( "FacilityRole", foreign_keys = [ facility_role_id ] )
    page_facility_role_page = relationship( "PageForm", foreign_keys = [ page_form_id ] )

class PageFormButton( StaticBase ):
    __tablename__ = 'page_form_button'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    page_form_id = Column( Integer, ForeignKey( 'page_form.id' ) )
    button_type = Column( String( 100 ) )
    button_location = Column( String( 100 ) )
    button_class = Column( String( 100 ) )
    button_value = Column( String( 100 ) )
    button_id = Column( String( 100 ) )
    special_props = Column( String( 255 ) )

    page_form_button_page_form = relationship( "PageForm", foreign_keys = [ page_form_id ] )

class PageFormButtonFacilityRole( StaticBase ):
    __tablename__ = 'page_form_button_facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_role_id = Column( Integer, ForeignKey( 'facility_role.id' ) )
    page_form_button_id = Column( Integer, ForeignKey( 'page_form_button.id' ) )

    page_form_button_facility_role_facility = relationship( "FacilityRole", foreign_keys = [ facility_role_id ] )
    page_form_button_facility_role_page_form = relationship( "PageFormButton", foreign_keys = [ page_form_button_id ] )

class TableObject( StaticBase ):
    __tablename__ = 'table_object'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    new_name_prefix = Column( String( 100 ), unique = True )
    new_name_id = Column( Integer )
    id_length = Column( Integer )

class TableObjectFacilityRole( StaticBase ):
    __tablename__ = 'table_object_facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_role_id = Column( Integer, ForeignKey( 'facility_role.id' ) )
    table_object_id = Column( Integer, ForeignKey( 'table_object.id' ) )
    module_id = Column( Integer, ForeignKey( 'module.id' ) )

    type_facility_role_facility = relationship( "FacilityRole", foreign_keys = [ facility_role_id ] )
    type_facility_role_type = relationship( "TableObject", foreign_keys = [ table_object_id ] )
    type_facility_role_module = relationship( "Module", foreign_keys = [ module_id ] )
    type_facility_role_unq = UniqueConstraint( 'facility_role_id', 'table_object_id' )

class TableObjectChildren( StaticBase ):
    __tablename__ = 'table_object_children'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    table_object_id = Column( Integer, ForeignKey( 'table_object.id' ) )
    child_table_object_id = Column( Integer, ForeignKey( 'table_object.id' ) )

    table_object_children_table_object = relationship( "TableObject", foreign_keys = [ table_object_id ] )
    table_object_children_child_table_object = relationship( "TableObject", foreign_keys = [ child_table_object_id ] )

class TableObjectChildrenFacilityRole( StaticBase ):
    __tablename__ = 'table_object_children_facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_role_id = Column( Integer, ForeignKey( 'facility_role.id' ) )
    table_object_children_id = Column( Integer, ForeignKey( 'table_object_children.id' ) )
    module_id = Column( Integer, ForeignKey( 'module.id' ) )

    table_object_children_facility_role_facility = relationship( "FacilityRole", foreign_keys = [ facility_role_id ] )
    table_object_children_facility_role_type = relationship( "TableObjectChildren", foreign_keys = [ table_object_children_id ] )
    table_object_children_facility_role_module = relationship( "Module", foreign_keys = [ module_id ] )
    table_object_children_facility_role_unq = UniqueConstraint( 'facility_role_id', 'table_object_id' )

class Field( StaticBase ):
    __tablename__ = 'field'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    field_name = Column( String( 100 ) )
    table_object_id = Column( Integer, ForeignKey( 'table_object.id' ) )
    data_type_id = Column( Integer, ForeignKey( 'data_type.id' ) )
    unique = Column( Boolean )
    primary_key = Column( Boolean )
    length = Column( Integer )
    default = Column( String( 255 ) )
    foreign_key_table_object_id = Column( Integer, ForeignKey( 'table_object.id' ) )
    foreign_key_field_id = Column( Integer, ForeignKey( 'field.id' ) )

    field_type = relationship( "TableObject", foreign_keys = [ table_object_id ] )
    field_data_type = relationship( "DataType", foreign_keys = [ data_type_id ] )
    field_foreign_key_table_object = relationship( "TableObject", foreign_keys = [ foreign_key_table_object_id ] )
    field_foreign_key_field = relationship( "Field", foreign_keys = [ foreign_key_field_id ] )

class FieldFacilityRole( StaticBase ):
    __tablename__ = 'field_facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_role_id = Column( Integer, ForeignKey( 'facility_role.id' ) )
    module_id = Column( Integer, ForeignKey( 'module.id' ) )
    field_id = Column( Integer, ForeignKey( 'field.id' ) )
    display_name = Column( String( 100 ) )
    visible = Column( Boolean )
    search_field = Column( Boolean )
    required = Column( Boolean )
    permission_id = Column( Integer, ForeignKey( 'permission.id' ) )

    field_facility_role_facility = relationship( "FacilityRole", foreign_keys = [ facility_role_id ] )
    field_facility_role_field = relationship( "Field", foreign_keys = [ field_id ] )
    field_facility_role_permission = relationship( "Permission", foreign_keys = [ permission_id ] )
    field_facility_role_unq = UniqueConstraint( 'facility_role_id', 'field_id', 'page_id' )
    field_facility_role_module = relationship( "Module", foreign_keys = [ module_id ] )

class DataType( StaticBase ):
    __tablename__ = 'data_type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )

class Permission( StaticBase ):
    __tablename__ = 'permission'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )

class Action( StaticBase ):
    __tablename__ = 'action'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    action_value = Column( String( 255 ) )

class NewUser( StaticBase ):
    __tablename__ = 'new_user'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    first_name = Column( String( 100 ) )
    last_name = Column( String( 100 ) )
    password_hash = Column( String( 100 ) )
    email = Column( String( 100 ) )
    organization = Column( String( 100 ) )
    address1 = Column( String( 100 ) )
    address2 = Column( String( 100 ) )
    city = Column( String( 100 ) )
    state = Column( String( 100 ) )
    postcode = Column( String( 100 ) )
    phone = Column( String( 100 ) )
    pi = Column( String( 100 ) )
    server = Column( String( 100 ) )
    directory = Column( String( 100 ) )

class TableQuery( StaticBase ):
    __tablename__ = 'table_query'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    display_name = Column( String(100) )

class TableQueryRender( StaticBase ):
    __tablename__ = 'table_query_render'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    table_query_id = Column( Integer, ForeignKey( 'table_query.id' ) )
    table_object_id = Column( Integer, ForeignKey( 'table_object.id' ) )
    page_form_facility_role_id = Column( Integer, ForeignKey(
        'page_form_facility_role.id' ) )

    table_query_render_page_form_facility_role = relationship( "PageFormFacilityRole", foreign_keys = [ page_form_facility_role_id ] )
    table_query_render_table_query = relationship( "TableQuery", foreign_keys = [ table_query_id ] )
    table_query_render_table_object = relationship( "TableObject", foreign_keys = [ table_object_id ] )

class TableQueryTableObject( StaticBase ):
    __tablename__ = 'table_query_table_object'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    table_query_id = Column( Integer, ForeignKey( 'table_query.id' ) )
    table_object_id = Column( Integer, ForeignKey( 'table_object.id' ) )

    table_query_type_type = relationship( "TableObject", foreign_keys = [ table_object_id ] )
    table_query_type_table_query = relationship( "TableQuery", foreign_keys = [ table_query_id ] )

class TableQueryField( StaticBase ):
    __tablename__ = 'table_query_field'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    table_query_id = Column( Integer, ForeignKey( 'table_query.id' ) )
    field_id = Column( Integer, ForeignKey( 'field.id' ) )
    display_name = Column( String( 100 ) )

    table_query_field_field = relationship( "Field", foreign_keys = [ field_id ] )
    table_query_field_table_query = relationship( "TableQuery", foreign_keys = [ table_query_id ] )

class TableQueryCriteria( StaticBase ):
    __tablename__ = 'table_query_criteria'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    table_query_id = Column( Integer, ForeignKey( 'table_query.id' ) )
    field_id = Column( Integer, ForeignKey( 'field.id' ) )
    value = Column( String( 255 ) )
    comparator = Column( String( 10 ) )

    table_query_criteria_table_query = relationship( "TableQuery", foreign_keys = [ table_query_id ] )
    table_query_criteria_field = relationship( "Field", foreign_keys = [ field_id ] )

class TableQueryOrder( StaticBase ):
    __tablename__ = 'table_query_order'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    table_query_id = Column( Integer, ForeignKey( 'table_query.id' ) )
    field_id = Column( Integer, ForeignKey( 'field.id' ) )
    direction = Column( String( 50 ) )

    table_query_order_field = relationship( "Field", foreign_keys = [ field_id ] )
    table_query_order_table_query = relationship( "TableQuery", foreign_keys = [ table_query_id ] )

class Module( StaticBase ):
    __tablename__ = 'module'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    url_prefix = Column( String( 50 ) )

class ModuleFacilityRole( StaticBase ):
    __tablename__ = 'module_facility_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    facility_role_id = Column( Integer, ForeignKey( 'facility_role.id' ) )
    module_id = Column( Integer, ForeignKey( 'module.id' ) )

    module_role_facility = relationship( "FacilityRole", foreign_keys = [ facility_role_id ] )
    module_facility_role_module = relationship( "Module", foreign_keys = [ module_id ] )
