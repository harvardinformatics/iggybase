from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from iggybase.extensions import lm
from iggybase.database import Base
from iggybase.mod_auth import constants as USER
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, relation
import datetime

class User( UserMixin, Base ):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer, ForeignKey( 'organization.id' ) )
    order = Column( Integer )
    password_hash = Column( String( 120 ) )
    first_name = Column( String( 50 ) )
    last_name = Column( String( 50 ) )
    email = Column( String( 120 ), unique = True )
    address_id = Column( Integer, ForeignKey( 'address.id' ) )
    home_page = Column( String( 50 ) )
    current_user_role_id = Column( Integer, ForeignKey( 'user_role.id' ) )

    user_user_role = relationship( "UserRole", foreign_keys = [ current_user_role_id ] )
    user_organization = relationship( "Organization", foreign_keys = [ organization_id ] )

    def get_id(self):
        return str( self.id )

    def set_password( self, password ):
        self.password_hash = generate_password_hash( password )

    def verify_password( self, password ):
        return check_password_hash( self.password_hash, password )

    @staticmethod
    def get_password_hash( password ):
        return generate_password_hash( password )

    def __init__( self, name = None, email = None ):
        self.name = name
        self.email = email

    def get_role( self ):
        return USER.ROLE[ self.role_id ]

    def __repr__( self ):
        return '<User %r>' % ( self.name )

class UserRole( Base ):
    __tablename__ = 'user_role'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer, ForeignKey( 'organization.id' ) )
    order = Column( Integer )
    user_id = Column( Integer, ForeignKey( 'user.id' ) )
    role_id = Column( Integer )
    director = Column( Boolean )
    manager = Column( Boolean )

    user_role_user = relationship( "User", foreign_keys = [ user_id ] )
    user_role_organization = relationship( "Organization", foreign_keys = [ organization_id ] )

class Organization( Base ):
    __tablename__ = 'organization'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer )
    order = Column( Integer )
    address_id = Column( Integer, ForeignKey( 'address.id' ) )
    billing_address_id = Column( Integer )
    organization_type_id = Column( Integer )
    parent_id = Column( Integer, ForeignKey( 'organization.id' ) )

    parent = relation( 'Organization', remote_side = [ id ] )

@lm.user_loader
def load_user( id ):
    return User.query.get( int( id ) )