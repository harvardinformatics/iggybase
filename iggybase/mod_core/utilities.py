from flask import abort
from importlib import import_module
from iggybase.tablefactory import TableFactory
from iggybase.mod_admin.models import TableObject
from iggybase.database import db_session
import logging

def get_column(module, table_name, field_name):
    table_model = get_table(table_name)
    return getattr(table_model, field_name)

def get_table(table_name):
    table = db_session.query(TableObject).filter_by(name=table_name).first()
    try:
        if table.admin_table_object == 1:
            module_model = import_module('iggybase.mod_admin.models')
        else:
            module_model = import_module('iggybase.models')
        table_object = getattr(module_model, TableFactory.to_camel_case(table_name))
    except AttributeError:
        logging.info('abort ' + table_name)
        abort(404)
    return table_object

def get_field_attr(table_query_field_obj, field_obj, attr):
    if table_query_field_obj and getattr(table_query_field_obj, attr):
        value = getattr(table_query_field_obj, attr)
    else:
        if attr == 'display_name':
            attr = 'field_name'
        value = getattr(field_obj, attr)
    return value
