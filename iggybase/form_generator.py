from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, email
from iggybase.mod_admin.models import TableObject, TableObjectFacilityRole, Field, FieldFacilityRole
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
from iggybase.database import admin_db_session

class FormGenerator( ):
    def __init__( self, module, table_object, active = 1 ):
        self.organization_access_control = OrganizationAccessControl( )
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

    def default_single_entry_form( self, instance_name  ):
        pass

    def default_multiple_entry_form( self, instance_names ):
        pass

    def default_parent_child_entry_form( self, parent_name ):
        pass
