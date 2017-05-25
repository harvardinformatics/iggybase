from iggybase.tablefactory import TableFactory
from iggybase.database import Base
import logging

table_factory = TableFactory()

tables = table_factory.table_objects()
for table_data in tables:
    globals()[table_data.TableObject.name] = table_data.TableObject
    globals()[table_data.TableObject.name].__module__ = __name__

    if (table_data.TableObject.admin_table is None or table_data.TableObject.admin_table == 0) and \
                    table_data.TableObject.name not in Base.metadata.tables:
        table_object_cols = table_factory.fields(table_data.TableObject.id)
        class_name = TableFactory.to_camel_case(table_data.TableObject.name)

        is_extended = False
        if getattr(table_data, 'Extended') is not None:
            is_extended = True

        extend_table = None
        extend_class = None
        if getattr(table_data, 'Extension') is not None:
            extend_table = table_data.Extension.name
            extend_class = globals()[TableFactory.to_camel_case(extend_table)]

        rows = table_factory.fields(table_data.TableObject.id)

        new_table = table_factory.table_object_factory(class_name, table_data.TableObject, table_object_cols,
                                                       extend_class, extend_table, is_extended)

        if new_table is not None:
            globals()[class_name] = new_table
            globals()[class_name].__module__ = __name__