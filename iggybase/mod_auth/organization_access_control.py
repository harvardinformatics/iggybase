from flask import g
from iggybase.database import db_session
from iggybase.mod_auth.models import load_user, UserRole, Organization
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
from importlib import import_module
import logging

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__ ( self, module ):
        self.org_ids = [ ]
        self.module = module

        if g.user is not None and not g.user.is_anonymous:
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
            module_model = import_module( 'iggybase.' + self.module + '.models' )
            table_object = getattr( module_model, table_name )

            field_data = self.facility_role_access_control.fields( table_data.id, self.module )

            if field_data is not None:
                columns = [ ]
                for row in  field_data:
                    if row.FieldFacilityRole.visible == 1:
                        columns.append( getattr( table_object, row.Field.field_name ).\
                                    label( row.FieldFacilityRole.display_name ) )

                results = db_session.query( *columns ).all( )

                return results

        return None

    def get_summary_data( self, table_name, query_data = None ):
        table_data = self.facility_role_access_control.has_access( 'TableObject', table_name )

        if table_data is not None:
            module_model = import_module( 'iggybase.' + self.module + '.models' )
            table_object = getattr( module_model, table_name )

            field_data = self.facility_role_access_control.fields( table_data.id, self.module )

            if field_data is not None:
                columns = [ ]
                for row in  field_data:
                    if row.Field.foreign_key_table_object_id is not None:
                        pass
                    elif row.FieldFacilityRole.visible == 1:
                        columns.append( getattr( table_object, row.Field.field_name ).\
                                    label( row.FieldFacilityRole.display_name ) )

                results = db_session.query( *columns ).all( )

                return results

        return None

    def get_row( self, table_name, row_name ):
        table_data = self.facility_role_access_control.has_access( 'TableObject', table_name )
        if table_data is not None:
            pass
        return None
