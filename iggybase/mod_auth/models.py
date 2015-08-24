from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from iggybase.extensions import lm
from iggybase.database import Base
from iggybase.mod_auth import constants as USER
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from iggybase.mod_core.models import Address
import datetime

class User( UserMixin, Base ):
    __tablename__ = 'user'
    id = Column( Integer, primary_key = True )
    name = Column( String( 50 ), unique = True )
    description = Column( String( 255 ) )
    date_created = Column( DateTime, default=datetime.datetime.utcnow )
    last_modified = Column( DateTime, default=datetime.datetime.utcnow )
    active = Column( Boolean )
    password_hash = Column( String( 120 ) )
    first_name = Column( String( 50 ) )
    last_name = Column( String( 50 ) )
    email = Column( String( 120 ), unique = True )
    address_id = Column( Integer, ForeignKey( 'address.id' ) )
    home_page = Column( String( 50 ) )
    role_id = Column( Integer, default = USER.READONLY )

    user_address = relationship( "Address", foreign_keys = [ address_id ] )

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

    def set_password( self, password ):
        self.password_hash = generate_password_hash( password )

    def verify_password( self, password ):
        return check_password_hash( self.password_hash, password )

    def __init__( self, name = None, email = None ):
        self.name = name
        self.email = email

    def get_id( self ):
        return self.id

    def get_active( self ):
        return self.active

    def get_role( self ):
        return USER.ROLE[ self.role_id ]

    def __repr__( self ):
        return '<User %r>' % ( self.name )


@lm.user_loader
def load_user( id ):
    return User.query.get( int( id ) )
