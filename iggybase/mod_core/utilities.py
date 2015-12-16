from importlib import import_module
from iggybase.tablefactory import TableFactory

def get_column(module, table_name, field_name):
    table_model = get_table(module, table_name)
    return getattr(table_model, field_name)

def get_table(module, table_name):
    module_model = import_module('iggybase.' + module + '.models')
    return getattr(module_model, TableFactory.to_camel_case(table_name))

def get_field_attr(table_query_field_obj, field_obj, attr):
    if table_query_field_obj and getattr(table_query_field_obj, attr):
        value = getattr(table_query_field_obj, attr)
    else:
        if attr == 'display_name':
            attr = 'field_name'
        value = getattr(field_obj, attr)
    return value
