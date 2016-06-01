from iggybase.tablefactory import TableFactory
import logging

table_factory = TableFactory()

tables = table_factory.table_objects()

for table_object in tables:
    class_name = TableFactory.to_camel_case(table_object.name)
    if class_name not in globals():
        new_table = table_factory.table_object_factory(class_name, table_object)

        if new_table is not None:
            globals()[class_name] = new_table
            globals()[class_name].__module__ = __name__