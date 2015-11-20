from flask.ext.wtf import Form
from types import new_class
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SelectField, ValidationError, DateField
from wtforms.validators import DataRequired, Length, email
from iggybase.mod_admin.models import TableObject, TableObjectFacilityRole, Field, FieldFacilityRole
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
from iggybase.database import admin_db_session
import logging

class FormGenerator( ):
    def __init__( self, module, table_object ):
        self.facility_role_access_control = FacilityRoleAccessControl( )
        self.organization_access_control = OrganizationAccessControl( module )
        self.table_object = table_object

    def input_field( self, field_data, value = None ):
        if field_data.Field.data_type_id == 1:
            return IntegerField( field_data.FieldFacilityRole.display_name, validators = [ DataRequired ] )
        elif field_data.Field.data_type_id == 2:
            return StringField( field_data.FieldFacilityRole.display_name, validators = [ DataRequired ] )
        elif field_data.Field.data_type_id == 3:
            return BooleanField( field_data.FieldFacilityRole.display_name, validators = [ DataRequired ] )
        elif field_data.Field.data_type_id == 4:
            return DateField( field_data.FieldFacilityRole.display_name, validators = [ DataRequired ] )
        elif field_data.Field.data_type_id == 5:
            return PasswordField( field_data.FieldFacilityRole.display_name, validators = [ DataRequired ] )
        elif field_data.Field.data_type_id == 6:
            return SelectField( field_data.FieldFacilityRole.display_name, validators = [ DataRequired ] )

    def default_single_entry_form( self, row_name = None ):
        if row_name is not None:
            data = self.organization_access_control.get_row( self.table_object, row_name )

        table_data = self.facility_role_access_control.has_access( 'TableObject', self.table_object )
        fields = self.facility_role_access_control.fields( table_data.id )

        classattr = { }
        for field in fields:
            classattr[ field.Field.field_name ] = self.input_field( field )

        newclass = new_class( 'DynamicForm', ( Form, ), { }, lambda ns: ns.update( classattr ) )

        return newclass( )

    def default_multiple_entry_form( self, row_names = None ):
        pass

    def default_parent_child_entry_form( self, parent_row_name = None ):
        pass
