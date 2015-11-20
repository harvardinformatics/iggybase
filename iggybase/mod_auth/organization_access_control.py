from flask import g
from iggybase.database import db_session
from iggybase.mod_auth.models import load_user, UserRole, Organization
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
from iggybase.mod_admin import models
import logging

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__ ( self, module ):
        self.org_ids = [ ]
        self.module = module

        if g.user is not None and not g.user.is_anonymous( ):
            self.user = load_user( g.user.id )
            self.user_role = db_session.query( UserRole ).filter_by( id = self.user.current_user_role_id ).first( )
            self.facility_role_access_control = FacilityRoleAccessControl( )
            self.org_ids.append( self.user_role.organization_id )

            self.get_child_organization( self.user_role.organization_id )
        else:
            self.user = None
            self.user_role = None

    def get_child_organization( self, parent_organization_id ):
        self.org_ids.append( parent_organization_id )

        child_orgs = db_session.query( Organization ).filter_by( parent_id = parent_organization_id ).all( )

        if child_orgs is None:
            return

        for child_org in child_orgs:
            self.get_child_organization( child_org.id )

        return

    def get_data( self, table_name, query_data = None ):
        table_data = self.facility_role_access_control.has_access( 'TableObject', table_name )
        if table_data is not None:
            field_data = self.facility_role_access_control.fields( table_data.id )

            select_clause = ''

            for row in  field_data:
                select_clause += '`' + row.Field.field_name + '` as `' + row.FieldFacilityRole.display_name + '`, '

            logging.info( 'select_clause: ' + select_clause )
            results = db_session.query( 'select ' + select_clause[ :-2 ] + ' from ' + table_data.name ).all( )

            return results

        return None
