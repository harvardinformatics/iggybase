from iggybase.tablefactory import TableFactory
from iggybase.mod_auth.facility_access_control import FacilityAccessControl
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl

table_factory = TableFactory( "mod_murray" )
facility_access_control = FacilityAccessControl( )

tables = facility_access_control.module_table_objects( "mod_murray" )

for table_object in tables:
    class_name = TableFactory.to_camel_case( table_object.name )

    globals()[ class_name ] = table_factory.table_object_factory ( class_name, table_object )

    globals()[ class_name ].__module__ = __name__

