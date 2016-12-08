from iggybase.tablefactory import TableFactory
from iggybase.database import Base
import logging

table_factory = TableFactory()

tables = table_factory.table_objects()
for table_object in tables:
    if table_object.TableObject.name not in Base.metadata.tables:
        is_base = False
        class_name = TableFactory.to_camel_case(table_object.TableObject.name)
        if getattr(table_object, 'Base') is not None:
            is_base = True
        extend_class = None
        if getattr(table_object, 'Extension') is not None:
            extend_class = globals()[TableFactory.to_camel_case(table_object.Extension.name)]
        new_table = table_factory.table_object_factory(class_name, table_object.TableObject, extend_class, is_base)

        if new_table is not None:
            globals()[class_name] = new_table
            globals()[class_name].__module__ = __name__
