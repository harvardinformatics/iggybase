from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from iggybase.extensions import lm
from iggybase.database import Base
from iggybase.mod_auth import constants as USER
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

class User( UserMixin, Base ):
    __tablename__ = 'user'
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
    home_page_variable = Column( String( 50 ) )
    role_id = Column( Integer, default = USER.READONLY )

    def is_authenticated( self ):
        return True

    def is_active( self ):
        return self.active

    def is_anonymous( self ):
        return False

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

class UserType( Base ):
    __tablename__ = 'user_type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer, ForeignKey( 'organization.id' ) )
    order = Column( Integer )
    director = Column( Boolean )
    manager = Column( Boolean )

class UserUserType( Base ):
    __tablename__ = 'user_user_type'
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    organization_id = Column( Integer, ForeignKey( 'organization.id' ) )
    order = Column( Integer )
    user_id = Column( Integer, ForeignKey( 'user.id' ) )
    user_type_id = Column( Integer, ForeignKey( 'user_type.id' ) )

    user_type_user = relationship( "User", foreign_keys = [ user_id ] )
    user_type_user_type = relationship( "UserType", foreign_keys = [ user_type_id ] )

@lm.user_loader
def load_user( id ):
    return User.query.get( int( id ) )