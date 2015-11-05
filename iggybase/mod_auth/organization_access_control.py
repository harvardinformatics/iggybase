from flask.ext.login import current_user
from iggybase.database import db_session
from iggybase.mod_auth.models import load_user, UserRole
import logging

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__ ( self ):
        if current_user.is_authenticated( ):
            self.user = load_user( current_user.id )
            self.user_role = db_session.query( UserRole ).filter_by( id = self.user.current_user_id ).first( )
        else:
            self.user = None
            self.user_role = None

    def table_object_rows( self, table_object_name, active = 1 ):
        pass


    def table_object_fields( self, table_object_id, active = 1 ):
        pass
