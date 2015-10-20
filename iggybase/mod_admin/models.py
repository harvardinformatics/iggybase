from iggybase.database import StaticBase
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from iggybase.mod_admin import constants as ADMIN
import datetime

class Group( StaticBase ):
    __tablename__ = 'group'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

class Role( StaticBase ):
    __tablename__ = 'role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )

class GroupRole( StaticBase ):
    __tablename__ = 'group_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_id = Column( Integer, ForeignKey( 'group.id' ) )
    role_id = Column( Integer, ForeignKey( 'role.id' ) )

    group_role_group = relationship( "Group", foreign_keys = [ group_id ] )
    group_role_role = relationship( "Role", foreign_keys = [ role_id ] )
    group_role_unq = UniqueConstraint( 'group_id', 'role_id' )

class Menu( StaticBase ):
    __tablename__ = 'menu'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    menu_type_id = Column( Integer, ForeignKey( 'menu_type.id' ) )

    menu_menu_type = relationship( "MenuType", foreign_keys = [ menu_type_id ] )

class MenuGroupRole( StaticBase ):
    __tablename__ = 'menu_group_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_role_id = Column( Integer, ForeignKey( 'group_role.id' ) )
    menu_id = Column( Integer, ForeignKey( 'menu.id' ) )
    order = Column( Integer )

    menu_group_role_group = relationship( "GroupRole", foreign_keys = [ group_role_id ] )
    menu_group_role_menu = relationship( "Menu", foreign_keys = [ menu_id ] )
    menu_group_role_unq = UniqueConstraint( 'group_role_id', 'menu_id' )

class MenuType( StaticBase ):
    __tablename__ = 'menu_type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

class MenuItem( StaticBase ):
    __tablename__ = 'menu_item'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ) )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    menu_item_value = Column( String( 250 ) )
    menu_id = Column( Integer, ForeignKey( 'menu.id' ) )

    menu_item_menu = relationship( "Menu", foreign_keys = [ menu_id ] )

class MenuItemGroupRole( StaticBase ):
    __tablename__ = 'menu_item_group_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_role_id = Column( Integer, ForeignKey( 'group_role.id' ) )
    menu_item_id = Column( Integer, ForeignKey( 'menu_item.id' ) )
    order = Column( Integer )

    menu_item_group_role_group = relationship( "GroupRole", foreign_keys = [ group_role_id ] )
    menu_item_group_role_menu_item = relationship( "MenuItem", foreign_keys = [ menu_item_id ] )
    menu_item_group_role_unq = UniqueConstraint( 'group_role_id', 'menu_item_id' )

class PageForm( StaticBase ):
    __tablename__ = 'page_form'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

class PageFormGroupRole( StaticBase ):
    __tablename__ = 'page_form_group_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_role_id = Column( Integer, ForeignKey( 'group_role.id' ) )
    page_form_id = Column( Integer, ForeignKey( 'page_form.id' ) )

    page_group_role_group = relationship( "GroupRole", foreign_keys = [ group_role_id ] )
    page_group_role_page = relationship( "PageForm", foreign_keys = [ page_form_id ] )

class PageFormButtons( StaticBase ):
    __tablename__ = 'page_form_buttons'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    page_form_id = Column( Integer, ForeignKey( 'page_form.id' ) )

    page_form_buttons_group_role_page = relationship( "PageForm", foreign_keys = [ page_form_id ] )

class PageFormButtonsGroupRole( StaticBase ):
    __tablename__ = 'page_form_buttons_group_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_role_id = Column( Integer, ForeignKey( 'group_role.id' ) )
    page_form_buttons_id = Column( Integer, ForeignKey( 'page_form_buttons.id' ) )
    order = Column( Integer )

    page_form_buttons_group_role_group = relationship( "GroupRole", foreign_keys = [ group_role_id ] )
    page_form_buttons_group_role_page_form = relationship( "PageFormButtons", foreign_keys = [ page_form_buttons_id ] )

class TableObject( StaticBase ):
    __tablename__ = 'table_object'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    new_name_prefix = Column( String( 100 ), unique = True )
    new_name_id = Column( Integer )
    id_length = Column( Integer )
    module = Column( String( 100 ) )

class TableObjectGroupRole( StaticBase ):
    __tablename__ = 'table_object_group_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_role_id = Column( Integer, ForeignKey( 'group_role.id' ) )
    table_object_id = Column( Integer, ForeignKey( 'table_object.id' ) )

    type_group_role_group = relationship( "GroupRole", foreign_keys = [ group_role_id ] )
    type_group_role_type = relationship( "TableObject", foreign_keys = [ table_object_id ] )
    type_group_role_unq = UniqueConstraint( 'group_role_id', 'table_object_id' )

class Field( StaticBase ):
    __tablename__ = 'field'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
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

class FieldGroupRole( StaticBase ):
    __tablename__ = 'field_group_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_role_id = Column( Integer, ForeignKey( 'group_role.id' ) )
    field_id = Column( Integer, ForeignKey( 'field.id' ) )
    display_name = Column( String( 100 ) )
    order = Column( Integer )
    visible = Column( Boolean )
    required = Column( Boolean )
    permission_id = Column( Integer, ForeignKey( 'permission.id' ) )

    field_group_role_group = relationship( "GroupRole", foreign_keys = [ group_role_id ] )
    field_group_role_field = relationship( "Field", foreign_keys = [ field_id ] )
    field_group_role_permission = relationship( "Permission", foreign_keys = [ permission_id ] )
    field_group_role_unq = UniqueConstraint( 'group_role_id', 'field_id', 'page_id' )

class DataType( StaticBase ):
    __tablename__ = 'data_type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

class Permission( StaticBase ):
    __tablename__ = 'permission'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

class Action( StaticBase ):
    __tablename__ = 'action'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    action_value = Column( String( 255 ) )

class ActionGroupRole( StaticBase ):
    __tablename__ = 'action_group_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_role_id = Column( Integer, ForeignKey( 'group_role.id' ) )
    action_id = Column( Integer, ForeignKey( 'action.id' ) )

    action_group_role_group = relationship( "GroupRole", foreign_keys = [ group_role_id ] )
    action_group_role_action = relationship( "Action", foreign_keys = [ action_id ] )
    action_group_role_unq = UniqueConstraint( 'group_role_id', 'action_id' )

class NewUser( StaticBase ):
    __tablename__ = 'new_user'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    first_name = Column( String( 100 ) )
    last_name = Column( String( 100 ) )
    password_hash = Column( String( 100 ) )
    email = Column( String( 100 ) )
    institution = Column( String( 100 ) )
    address1 = Column( String( 100 ) )
    address2 = Column( String( 100 ) )
    city = Column( String( 100 ) )
    state = Column( String( 100 ) )
    postcode = Column( String( 100 ) )
    phone = Column( String( 100 ) )
    pi = Column( String( 100 ) )
    group = Column( String( 100 ) )
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

class TableQueryType( StaticBase ):
    __tablename__ = 'table_query_type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
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
    table_query_id = Column( Integer, ForeignKey( 'table_query.id' ) )
    field_id = Column( Integer, ForeignKey( 'field.id' ) )

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
    table_query_id = Column( Integer, ForeignKey( 'table_query.id' ) )
    criteria = Column( String( 255 ) )

    table_query_criteria_table_query = relationship( "TableQuery", foreign_keys = [ table_query_id ] )

class TableQueryOrder( StaticBase ):
    __tablename__ = 'table_query_order'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    table_query_id = Column( Integer, ForeignKey( 'table_query.id' ) )
    field_id = Column( Integer, ForeignKey( 'field.id' ) )
    direction = Column( String( 50 ) )

    table_query_order_field = relationship( "Field", foreign_keys = [ field_id ] )
    table_query_order_table_query = relationship( "TableQuery", foreign_keys = [ table_query_id ] )
