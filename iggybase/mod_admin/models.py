from iggybase.database import StaticBase
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from iggybase.mod_admin import constants as ADMIN
import datetime

class Lab( StaticBase ):
    __tablename__ = 'lab'
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

class LabRole( StaticBase ):
    __tablename__ = 'lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_id = Column( Integer, ForeignKey( 'lab.id' ) )
    role_id = Column( Integer, ForeignKey( 'role.id' ) )

    lab_role_lab = relationship( "Lab", foreign_keys = [ lab_id ] )
    lab_role_role = relationship( "Role", foreign_keys = [ role_id ] )
    lab_role_unq = UniqueConstraint( 'lab_id', 'role_id' )

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

class MenuLabRole( StaticBase ):
    __tablename__ = 'menu_lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_role_id = Column( Integer, ForeignKey( 'lab_role.id' ) )
    menu_id = Column( Integer, ForeignKey( 'menu.id' ) )

    menu_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    menu_lab_role_menu = relationship( "Menu", foreign_keys = [ menu_id ] )
    menu_lab_role_unq = UniqueConstraint( 'lab_role_id', 'menu_id' )

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

class MenuItemLabRole( StaticBase ):
    __tablename__ = 'menu_item_lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_role_id = Column( Integer, ForeignKey( 'lab_role.id' ) )
    menu_item_id = Column( Integer, ForeignKey( 'menu_item.id' ) )

    menu_item_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    menu_item_lab_role_menu_item = relationship( "MenuItem", foreign_keys = [ menu_item_id ] )
    menu_item_lab_role_unq = UniqueConstraint( 'lab_role_id', 'menu_item_id' )

class PageForm( StaticBase ):
    __tablename__ = 'page_form'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

class PageFormLabRole( StaticBase ):
    __tablename__ = 'page_form_lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_role_id = Column( Integer, ForeignKey( 'lab_role.id' ) )
    page_form_id = Column( Integer, ForeignKey( 'page_form.id' ) )

    page_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    page_lab_role_page = relationship( "PageForm", foreign_keys = [ page_form_id ] )

class PageFormButtons( StaticBase ):
    __tablename__ = 'page_form_buttons'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

class IggyFormButtonsLabRole( StaticBase ):
    __tablename__ = 'page_form_buttons_lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_role_id = Column( Integer, ForeignKey( 'lab_role.id' ) )
    page_form_buttons_id = Column( Integer, ForeignKey( 'page_form_buttons.id' ) )

    page_form_buttons_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    page_form_buttons_lab_role_page = relationship( "PageForm", foreign_keys = [ page_form_buttons_id ] )

class Type( StaticBase ):
    __tablename__ = 'type'
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

class TypeLabRole( StaticBase ):
    __tablename__ = 'type_lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_role_id = Column( Integer, ForeignKey( 'lab_role.id' ) )
    type_id = Column( Integer, ForeignKey( 'type.id' ) )

    type_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    type_lab_role_type = relationship( "Type", foreign_keys = [ type_id ] )
    type_lab_role_unq = UniqueConstraint( 'lab_role_id', 'type_id' )

class Field( StaticBase ):
    __tablename__ = 'field'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    type_id = Column( Integer, ForeignKey( 'type.id' ) )
    data_type_id = Column( Integer, ForeignKey( 'data_type.id' ) )
    unique = Column( Boolean )
    primary_key = Column( Boolean )
    length = Column( Integer )
    default = Column( String( 255 ) )
    foreign_key_type_id = Column( Integer, ForeignKey( 'type.id' ) )
    foreign_key_field_id = Column( Integer, ForeignKey( 'field.id' ) )

    field_type = relationship( "Type", foreign_keys = [ type_id ] )
    field_data_type = relationship( "DataType", foreign_keys = [ data_type_id ] )
    field_foreign_key_type = relationship( "Type", foreign_keys = [ foreign_key_type_id ] )
    field_foreign_key_field = relationship( "Field", foreign_keys = [ foreign_key_field_id ] )

class FieldLabRole( StaticBase ):
    __tablename__ = 'field_lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_role_id = Column( Integer, ForeignKey( 'lab_role.id' ) )
    field_id = Column( Integer, ForeignKey( 'field.id' ) )
    display_name = Column( String( 100 ) )
    order = Column( Integer )
    visible = Column( Boolean )
    required = Column( Boolean )
    permission_id = Column( Integer, ForeignKey( 'permission.id' ) )

    field_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    field_lab_role_field = relationship( "Field", foreign_keys = [ field_id ] )
    field_lab_role_permission = relationship( "Permission", foreign_keys = [ permission_id ] )
    field_lab_role_unq = UniqueConstraint( 'lab_role_id', 'field_id', 'page_id' )

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

class ActionLabRole( StaticBase ):
    __tablename__ = 'action_lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_role_id = Column( Integer, ForeignKey( 'lab_role.id' ) )
    action_id = Column( Integer, ForeignKey( 'action.id' ) )

    action_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    action_lab_role_action = relationship( "Action", foreign_keys = [ action_id ] )
    action_lab_role_unq = UniqueConstraint( 'lab_role_id', 'action_id' )

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
    type_id = Column( Integer, ForeignKey( 'type.id' ) )

    table_query_type_type = relationship( "Type", foreign_keys = [ type_id ] )
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
