from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from iggybase import lm
from iggybase.database import Base
from iggybase.mod_auth import constants as USER
from iggybase.mod_core.models import Address
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class User( UserMixin, Base ):
    __tablename__ = 'user'
    user_id = Column( Integer, primary_key = True )
    login_name = Column( String( 50 ), unique = True )
    password_hash = Column( String( 120 ) )
    first_name = Column( String( 50 ) )
    last_name = Column( String( 50 ) )
    email = Column( String( 120 ), unique = True )
    description = Column( String( 250 ) )
    address_id = Column( Integer, ForeignKey( 'address.address_id' ) )
    home_page = Column( String( 50 ) )
    role_id = Column( Integer, ForeignKey( 'role.role_id' ), default = USER.READONLY )
    active = Column( Boolean )

    user_address = relationship( "Address", foreign_keys = [ address_id ] )

    def set_password( self, password ):
        self.password_hash = generate_password_hash( password )

    def verify_password( self, password ):
        return check_password_hash( self.password_hash, password )

    def __init__( self, login_name = None, password = None, email = None ):
        self.login_name = login_name
        self.email = email
        self.set_password( password )

    def get_id( self ):
        return self.user_id

    def get_active( self ):
        return self.active

    def get_role( self ):
        return USER.ROLE[ self.role_id ]

    def __repr__( self ):
        return '<User %r>' % ( self.login_name )

@lm.user_loader
def load_user( user_id ):
    return User.query.get( int( user_id ) )

class role( Base ):
    __tablename__ = 'role'
    role_id = Column( Integer, primary_key = True )
    role_name = Column( String( 100 ), unique = True )
    description = Column( String( 255 ) )
    active = Column( Boolean )

    def get_active( self ):
        return self.active
