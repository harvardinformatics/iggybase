from iggybase.tablefactory import TableFactory
from iggybase.mod_auth.facility_access_control import FacilityAccessControl
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl

table_factory = TableFactory( "mod_murray_lab" )
facility_access_control = FacilityAccessControl( )

tables = facility_access_control.module_table_objects( "mod_murray_lab" )

for table_object in tables:
    class_name = table_factory.to_camel_case( table_object.name )

    globals()[ class_name ] = table_factory.table_object_factory ( class_name, table_object )

    globals()[ class_name ].__module__ = __name__


def table_object_rows( self, module, table_object_name, active = 1, **fields ):
    pass

