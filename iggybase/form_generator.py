from flask.ext.wtf import Form
from types import new_class
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SelectField, ValidationError, DateField,\
    HiddenField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, email
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
import logging

class ReadonlyStringField( StringField ):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault( 'readonly', True )
        return super( ReadonlyStringField, self ).__call__( *args, **kwargs )

class ReadonlyTextAreaField( TextAreaField ):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault( 'readonly', True )
        return super( ReadonlyTextAreaField, self ).__call__( *args, **kwargs )

class ReadonlyIntegerField( IntegerField ):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault( 'readonly', True )
        return super( ReadonlyIntegerField, self ).__call__( *args, **kwargs )

class ReadonlyBooleanField( BooleanField ):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault( 'readonly', True )
        return super( ReadonlyBooleanField, self ).__call__( *args, **kwargs )

class FormGenerator( ):
    def __init__( self, module, table_object ):
        self.facility_role_access_control = FacilityRoleAccessControl( )
        self.organization_access_control = OrganizationAccessControl( module )
        self.table_object = table_object

    def input_field( self, field_data, value = None ):
        validators = [ ]
        if field_data.FieldFacilityRole.required == 1:
            validators.append( DataRequired( ) )

        if field_data.Field.length is not None and field_data.Field.data_type_id == 2:
            validators.append( Length( 0, field_data.Field.length ) )

        if "email" in field_data.Field.field_name:
            validators.append( email( ) )

        if field_data.FieldFacilityRole.permission_id == 2:
            if field_data.Field.data_type_id == 1:
                wtf_class = IntegerField
            elif field_data.Field.data_type_id == 3:
                wtf_class = BooleanField
            elif field_data.Field.data_type_id == 4:
                wtf_class = DateField
            elif field_data.Field.data_type_id == 5:
                wtf_class = PasswordField
            elif field_data.Field.data_type_id == 6:
                wtf_class = SelectField
            elif field_data.Field.data_type_id == 7:
                wtf_class = FileField
            elif field_data.Field.data_type_id == 8:
                wtf_class = TextAreaField
            else:
                wtf_class = StringField
        else:
            if field_data.Field.data_type_id == 1:
                wtf_class = ReadonlyIntegerField
            elif field_data.Field.data_type_id == 3:
                wtf_class = ReadonlyBooleanField
            elif field_data.Field.data_type_id == 4:
                wtf_class = ReadonlyTextAreaField
            else:
                wtf_class = ReadonlyStringField

        if field_data.FieldFacilityRole.visible != 1:
            if value is not None:
                wtf_field = HiddenField( field_data.FieldFacilityRole.display_name, default = value )
            else:
                wtf_field = HiddenField( field_data.FieldFacilityRole.display_name )
        else:
            if value is not None:
                wtf_field = wtf_class( field_data.FieldFacilityRole.display_name, validators, default = value )
            else:
                wtf_field = wtf_class( field_data.FieldFacilityRole.display_name, validators )

        return wtf_field

    def default_single_entry_form( self, row_name = 'new' ):
        if row_name != 'new':
            data = self.organization_access_control.get_row( self.table_object, row_name )

        table_data = self.facility_role_access_control.has_access( 'TableObject', self.table_object )

        fields = self.facility_role_access_control.fields( table_data.id )

        table_field = HiddenField( 'table_object_01', default = self.table_object )
        row_field = HiddenField( 'row_name_01', default = row_name )
        entry_field = HiddenField( 'entry_01', default = 'single' )

        classattr = { 'table_object': table_field, 'row_name': row_field, 'entry': entry_field }

        for field in fields:
            value = None
            if row_name != 'new':
                value = getattr( data, field.Field.field_name )

            classattr[ field.Field.field_name + '_01' ] = self.input_field( field, value )

        newclass = new_class( 'DynamicForm', ( Form, ), { }, lambda ns: ns.update( classattr ) )

        return newclass( )

    def default_multiple_entry_form( self, row_names = None ):
        pass

    def default_parent_child_entry_form( self, parent_row_name = None ):
        pass
