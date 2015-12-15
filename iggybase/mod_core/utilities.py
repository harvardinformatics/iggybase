from importlib import import_module
from iggybase.tablefactory import TableFactory

def get_column(module, table_name, field_name):
    table_model = get_table(module, table_name)
    return getattr(table_model, field_name)

def get_table(module, table_name):
    module_model = import_module('iggybase.' + module + '.models')
    return getattr(module_model, TableFactory.to_camel_case(table_name))
