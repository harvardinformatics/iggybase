from iggybase.tablefactory import TableFactory
import logging

table_factory = TableFactory( "mod_core" )

tables = table_factory.facility_access_control.module_table_objects( "mod_core" )

for table_object in tables:
    class_name = TableFactory.to_camel_case( table_object.name )

    globals()[ class_name ] = table_factory.table_object_factory ( class_name, table_object )

    globals()[ class_name ].__module__ = __name__

