from iggybase.database import StaticBase
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from iggybase.mod_admin import constants as STATIC

class Lab( StaticBase ):
    __tablename__ = 'lab'
    lab_id = Column( Integer, primary_key = True )
    lab_name = Column( String( 100 ), unique = True )
    lab_description = Column( String( 250 ) )
    active = Column( Boolean )

    def get_id( self ):
        return self.lab_id

    def get_active( self ):
        return self.active

class Iggybase_Instance( StaticBase ):
    __tablename__ = 'iggybase_instance'
    instance_id = Column( Integer, primary_key = True )
    instance_name = Column( String( 100 ), unique = True )
    instance_description = Column( String( 250 ) )
    database = Column( String( 250 ) )
    lab_id = Column ( Integer, ForeignKey( 'lab.lab_id' ) )
    active = Column( Boolean )

    instance_lab = relationship( "Lab", foreign_keys = [ lab_id ] )

    def get_id( self ):
        return self.instance_id

    def get_active( self ):
        return self.active

class Menu( StaticBase ):
    __tablename__ = 'menu'
    menu_id = Column( Integer, primary_key = True )
    menu_name = Column( String( 100 ), unique = True )
    lab_id = Column ( Integer, ForeignKey( 'lab.lab_id' ) )
    active = Column( Boolean )

    menu_lab = relationship( "Lab", foreign_keys = [ lab_id ] )

    def get_id( self ):
        return self.menu_id

    def get_active( self ):
        return self.active

class Menu_Item( StaticBase ):
    __tablename__ = 'menu_item'
    menu_item_id = Column( Integer, primary_key = True )
    menu_item_name = Column( String( 100 ) )
    menu_item_description = Column( String( 250 ) )
    menu_item_value = Column( String( 250 ) )
    lab_id = Column ( Integer, ForeignKey( 'lab.lab_id' ) )
    menu_id = Column( Integer, ForeignKey( 'menu.menu_id' ) )
    active = Column( Boolean )

    menu_item_lab = relationship( "Lab", foreign_keys = [ lab_id ] )
    menu_item_menu = relationship( "Menu", foreign_keys = [ menu_id ] )

    def get_id( self ):
        return self.menu_item_id

    def get_active( self ):
        return self.active

class Type( StaticBase ):
    __tablename__ = 'type'
    type_id = Column( Integer, primary_key = True )
    type_name = Column( String( 100 ), unique = True )
    lab_id = Column ( Integer, ForeignKey( 'lab.lab_id' ) )
    active = Column( Boolean )

    type_lab = relationship( "Lab", foreign_keys = [ lab_id ] )

    def get_id( self ):
        return self.type_id

    def get_active( self ):
        return self.active

class Field( StaticBase ):
    __tablename__ = 'field'
    field_id = Column( Integer, primary_key = True )
    field_name = Column( String( 100 ), unique = True )
    type_id = Column( Integer, ForeignKey( 'type.type_id' ) )
    lab_id = Column ( Integer, ForeignKey( 'lab.lab_id' ) )
    active = Column( Boolean )

    field_lab = relationship( "Lab", foreign_keys = [ lab_id ] )
    type = relationship( "Type", foreign_keys = [ type_id ] )

    def get_id( self ):
        return self.field_id

    def get_active( self ):
        return self.active

class Page( StaticBase ):
    __tablename__ = 'page'
    page_id = Column( Integer, primary_key = True )
    page_name = Column( String( 100 ), unique = True )
    lab_id = Column ( Integer, ForeignKey( 'lab.lab_id' ) )
    active = Column( Boolean )

    page_lab = relationship( "Lab", foreign_keys = [ lab_id ] )

    def get_id( self ):
        return self.page_id

    def get_active( self ):
        return self.active
