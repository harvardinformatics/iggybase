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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Role( StaticBase ):
    __tablename__ = 'role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Iggybase_Instance( StaticBase ):
    __tablename__ = 'iggybase_instance'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    host_name = Column( String( 250 ) )
    root_dir = Column( String( 250 ) )
    database = Column( String( 250 ) )
    lab_id = Column ( Integer, ForeignKey( 'lab.id' ) )

    instance_lab = relationship( "Lab", foreign_keys = [ lab_id ] )
    host_root = UniqueConstraint( 'host_name', 'root_dir' )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class MenuType( StaticBase ):
    __tablename__ = 'menu_type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

    def get_active( self ):
        return self.active

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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Page( StaticBase ):
    __tablename__ = 'page'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

    def get_active( self ):
        return self.active

class PageLabRole( StaticBase ):
    __tablename__ = 'page_lab_role'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    lab_role_id = Column( Integer, ForeignKey( 'lab_role.id' ) )
    page_id = Column( Integer, ForeignKey( 'page.id' ) )

    page_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    page_lab_role_page = relationship( "Page", foreign_keys = [ page_id ] )
    page_lab_role_unq = UniqueConstraint( 'lab_role_id', 'page_id' )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Type( StaticBase ):
    __tablename__ = 'type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Field( StaticBase ):
    __tablename__ = 'field'
    id = Column( Integer, primary_key = True )
    field_name = Column( String( 100 ), unique = True )
    field_description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    type_id = Column( Integer, ForeignKey( 'type.id' ) )

    field_type = relationship( "Type", foreign_keys = [ type_id ] )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

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
    page_id = Column( Integer, ForeignKey( 'page.id' ) )
    visible = Column( Boolean )
    required = Column( Boolean )
    permission_id = Column( Integer, ForeignKey( 'permission.id' ) )
    type_id = Column( Integer, ForeignKey( 'type.id' ) )

    field_lab_role_lab = relationship( "LabRole", foreign_keys = [ lab_role_id ] )
    field_lab_role_field = relationship( "Field", foreign_keys = [ field_id ] )
    field_lab_role_page = relationship( "Page", foreign_keys = [ page_id ] )
    field_lab_role_permission = relationship( "Permission", foreign_keys = [ permission_id ] )
    field_lab_role_type = relationship( "Type", foreign_keys = [ type_id ] )
    field_lab_role_unq = UniqueConstraint( 'lab_role_id', 'field_id', 'page_id' )

    def get_active( self ):
        return self.active

class Permission( StaticBase ):
    __tablename__ = 'permission'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Action( StaticBase ):
    __tablename__ = 'action'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    action_value = Column( String( 255 ) )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

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

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active