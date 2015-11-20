from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, email
from iggybase.mod_admin.models import TableObject, TableObjectFacilityRole, Field, FieldFacilityRole
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
from iggybase.database import admin_db_session
import logging

class FormGenerator( ):
    def __init__( self, module, table_object, active = 1 ):
        self.facility_role_access_control = FacilityRoleAccessControl( )
        self.organization_access_control = OrganizationAccessControl( module )
        self.active = active
        self.table_object = table_object
        self.form = Form

    def textbox_input( self, field, value ):
        pass

    def checkbox_input( self, field, value ):
        pass

    def select_input( self, field, value ):
        pass

    def file_input( self, field, value ):
        pass

    def password_input( self, field, value ):
        pass

    def default_single_entry_form( self, row_name = None ):
        data = self.organization_access_control.get_data( 'table_object' )
        logging.info( data )

    def default_multiple_entry_form( self, row_name = None ):
        pass

    def default_parent_child_entry_form( self, parent_row_name = None ):
        pass
