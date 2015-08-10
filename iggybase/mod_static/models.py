from iggybase.database import Base, StaticBase
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from iggybase.mod_static import constants as STATIC

class lab( StaticBase ):
    __tablename__ = 'lab'
    lab_id = Column( Integer, primary_key = True )
    lab_name = Column( String( 100 ), unique = True )
    lab_description = Column( String( 250 ) )
    active = Column( Boolean )

class instance( StaticBase ):
    __tablename__ = 'lab'
    instance_id = Column( Integer, primary_key = True )
    instance_name = Column( String( 100 ), unique = True )
    instance_description = Column( String( 250 ) )
    lab_id = Column ( Integer )
    active = Column( Boolean )

    instance_lab = relationship( "lab", foreign_keys = [ lab_id ] )

class menu( StaticBase ):
    __tablename__ = 'menu'
    menu_id = Column( Integer, primary_key = True )
    menu_name = Column( String( 100 ), unique = True )
    lab_id = Column ( Integer )
    active = Column( Boolean )

    menu_lab = relationship( "lab", foreign_keys = [ lab_id ] )

class menu_item( StaticBase ):
    __tablename__ = 'menu_item'
    menu_item_id = Column( Integer, primary_key = True )
    menu_item_name = Column( String( 100 ) )
    menu_item_description = Column( String( 250 ) )
    menu_item_value = Column( String( 250 ) )
    lab_id = Column ( Integer )
    menu_id = Column( Integer )
    active = Column( Boolean )

    menu_item_lab = relationship( "lab", foreign_keys = [ lab_id ] )
    menu_id = relationship( "menu", foreign_keys = [ menu_id ] )

class type( StaticBase ):
    __tablename__ = 'type'
    type_id = Column( Integer, primary_key = True )
    type_name = Column( String( 100 ), unique = True )
    lab_id = Column ( Integer )
    active = Column( Boolean )

    type_lab = relationship( "lab", foreign_keys = [ lab_id ] )

class field( StaticBase ):
    __tablename__ = 'field'
    field_id = Column( Integer, primary_key = True )
    field_name = Column( String( 100 ), unique = True )
    type_id = Column( Integer )
    lab_id = Column ( Integer )
    active = Column( Boolean )

    field_lab = relationship( "lab", foreign_keys = [ lab_id ] )
    type = relationship( "type", foreign_keys = [ type_id ] )

class page( StaticBase ):
    __tablename__ = 'page'
    page_id = Column( Integer, primary_key = True )
    page_name = Column( String( 100 ), unique = True )
    lab_id = Column ( Integer )
    active = Column( Boolean )

    page_lab = relationship( "lab", foreign_keys = [ lab_id ] )
