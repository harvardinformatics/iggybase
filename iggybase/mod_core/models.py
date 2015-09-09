from iggybase.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from iggybase.mod_core import constants as CORE
import datetime

class Group( Base ):
    __tablename__ = 'group'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    address_id = Column( Integer, ForeignKey( 'address.id' ) )
    billing_address_id = Column( Integer, ForeignKey( 'address.id' ) )

    group_billing_address = relationship( "Address", foreign_keys = [ billing_address_id ] )
    group_address = relationship( "Address", foreign_keys = [ address_id ] )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Institution( Base ):
    __tablename__ = 'institution'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    address_id = Column( Integer, ForeignKey( 'address.id' ) )

    institution_address = relationship( "Address", foreign_keys = [ address_id ] )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class GroupPI( Base ):
    __tablename__ = 'group_pi'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_id = Column( Integer, ForeignKey( 'group.id' ) )
    user_id = Column( Integer, ForeignKey( 'user.id' ) )

    group_pi_group = relationship( "Group", foreign_keys = [ group_id ] )
    group_pi_user = relationship( "User", foreign_keys = [ user_id ] )
    group_pi_unq = UniqueConstraint( 'group_id', 'user_id' )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class GroupLabAdmin( Base ):
    __tablename__ = 'group_lab_admin'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_id = Column( Integer, ForeignKey( 'group.id' ) )
    user_id = Column( Integer, ForeignKey( 'user.id' ) )

    group_lab_admin_group = relationship( "Group", foreign_keys = [ group_id ] )
    group_lab_admin_user = relationship( "User", foreign_keys = [ user_id ] )
    group_lab_admin_unq = UniqueConstraint( 'group_id', 'user_id' )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class GroupInstitution( Base ):
    __tablename__ = 'group_institution'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    group_id = Column( Integer, ForeignKey( 'group.id' ) )
    institution_id = Column( Integer, ForeignKey( 'institution.id' ) )

    group_institution_group = relationship( "Group", foreign_keys = [ group_id ] )
    group_institution_institution = relationship( "Institution", foreign_keys = [ institution_id ] )
    group_institution_unq = UniqueConstraint( 'group_id', 'institution_id' )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Address( Base ):
    __tablename__ = 'address'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    address_1 = Column( String( 100 ) )
    address_2 = Column( String( 100 ) )
    city = Column( String( 100 ) )
    state = Column( String( 100 ) )
    postcode = Column( String( 100 ) )
    country = Column( String( 100 ) )

    def __init__( self, address_1 = None, city = None, state = None, postcode = None ):
        self.address_1 = address_1
        self.city = city
        self.state = state
        self.postcode = postcode

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Building( Base ):
    __tablename__ = 'building'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    address_id = Column( Integer, ForeignKey( 'address.id' ) )

    building_address = relationship( "Address", foreign_keys = [ address_id ] )

    def get_active( self ):
        return self.active

class Room( Base ):
    __tablename__ = 'room'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    building_id = Column( Integer, ForeignKey( 'building.id' ) )
    active = Column( Boolean )

    room_building = relationship( "Building", foreign_keys = [ building_id ] )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

class Container( Base ):
    __tablename__ = 'container'
    id = Column( Integer, primary_key = True )
    name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default = datetime.datetime.utcnow )
    last_modified = Column( DateTime, default = datetime.datetime.utcnow )
    active = Column( Boolean )
    rows = Column( Integer )
    columns = Column( Integer )
    building_id = Column( Integer, ForeignKey( 'building.id' ) )

    container_building = relationship( "Building", foreign_keys = [ building_id ] )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active
