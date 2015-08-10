from iggybase.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from iggybase.mod_core import constants as CORE

class group( Base ):
    __tablename__ = 'group'
    group_id = Column( Integer, primary_key = True )
    group_name = Column( String( 100 ), unique = True )
    address_id = Column( Integer, ForeignKey( 'address.address_id' ) )
    billing_address_id = Column( Integer, ForeignKey( 'address.address_id' ) )
    active = Column( Boolean )

    billing_address = relationship( "address", foreign_keys = [ billing_address_id ] )
    address = relationship( "address", foreign_keys = [ address_id ] )

class institution( Base ):
    __tablename__ = 'institution'
    institution_id = Column( Integer, primary_key = True )
    institution_name = Column( String( 100 ), unique = True )
    address_id = Column( Integer )
    active = Column( Boolean )

class group_pi( Base ):
    __tablename__ = 'group_pi'
    group_id = Column( Integer, ForeignKey( 'group.group_id' ), primary_key = True )
    user_id = Column( Integer, ForeignKey( 'user.user_id' ), primary_key = True )

class group_institution( Base ):
    __tablename__ = 'group_institution'
    group_id = Column( Integer, ForeignKey( 'group.group_id' ), primary_key = True )
    institution_id = Column( Integer, ForeignKey( 'institution.institution_id' ), primary_key = True )

class address( Base ):
    __tablename__ = 'address'
    address_id = Column( Integer, primary_key = True )
    address_1 = Column( String( 100 ) )
    address_2 = Column( String( 100 ) )
    city = Column( String( 100 ) )
    state = Column( String( 100 ) )
    postcode = Column( String( 100 ) )
    country = Column( String( 100 ) )
    active = Column( Boolean )

class building( Base ):
    __tablename__ = 'building'
    building_id = Column( Integer, primary_key = True )
    building_name = Column( String( 100 ), unique = True )
    building_desctiption = Column( String( 250) )
    address_id = Column( Integer )

    address = relationship( "address", foreign_keys = [ address_id ] )

class room( Base ):
    __tablename__ = 'room'
    room_id = Column( Integer, primary_key = True )
    room_name = Column( String( 100 ), unique = True )
    room_description = Column( String( 250) )
    building_id = Column( Integer )

    building = relationship( "building", foreign_keys = [ building_id ] )
