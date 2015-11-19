from flask.ext.login import current_user
from iggybase.database import db_session
from iggybase.mod_auth.models import load_user, UserRole, Organization
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
import logging

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__ ( self ):
        self.org_ids = [ ]

        if current_user.is_anonymous( ):
            self.user = None
            self.user_role = None
        else:
            self.user = load_user( current_user.id )
            self.user_role = db_session.query( UserRole ).filter_by( id = self.user.current_user_role_id ).first( )
            self.org_ids.append( self.user_role.organization_id )

            self.get_child_organization( self.user_role.organization_id )

    def get_child_organization( self, parent_organization_id ):
        self.org_ids.append( parent_organization_id )

        child_orgs = db_session.query( Organization ).filter_by( parent_id = parent_organization_id ).all( )

        if child_orgs is None:
            return

        for child_org in child_orgs:
            self.get_child_organization( child_org.id )

        return