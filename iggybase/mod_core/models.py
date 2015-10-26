from iggybase.modelfactory import table_object_factory, to_camel_case
from iggybase.mod_auth.facility_access_control import FacilityAccessControl
import logging

facility_access_control = FacilityAccessControl( )

tables = facility_access_control.module_table_objects( 'mod_core' )

for table_object in tables:

    #logging.info( 'table name: ' + to_camel_case( table_object.name ) )

    #colnames = [ row.field_name for row in table_object_cols ]

    class_name = to_camel_case( table_object.name )

    table_object_factory ( class_name, table_object )