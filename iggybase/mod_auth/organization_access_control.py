from flask.ext.login import current_user
from iggybase.database import db_session
from iggybase.mod_auth.models import load_user, UserUserType
from iggybase.mod_core import models
from iggybase.mod_admin.models import TableObject
from config import get_config
import logging

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__ ( self ):
        conf = get_config( )

        self.user = load_user( current_user.id )

        self.orgs = db_session.query( UserUserType ).filter_by( user_id = self.user.id ).all( )

    def table_rows( self, tablename, active = 1 ):
        pass


    def __table_fields( self, table_object_id, active = 1 ):
        pass
