from flask import abort, request
from importlib import import_module
from iggybase.tablefactory import TableFactory
from iggybase.mod_admin.models import TableObject
from iggybase.database import db_session
import logging

def get_column(module, table_name, field_name):
    table_model = get_table(table_name)
    return getattr(table_model, field_name)

def get_table(table_name):
    session = db_session()
    table = session.query(TableObject).filter_by(name=table_name).first()

    try:
        if table.admin_table == 1:
            module_model = import_module('iggybase.mod_admin.models')
        else:
            module_model = import_module('iggybase.models')
        table_object = getattr(module_model, TableFactory.to_camel_case(table_name))
    except AttributeError:
        logging.info('abort ' + table_name)
        abort(404)
    finally:
        session.commit()

    return table_object

def get_field_attr(field, table_query_field, attr):
    if table_query_field and getattr(table_query_field, attr):
        value = getattr(table_query_field, attr)
    else:
        if attr == 'display_name':
            attr = 'field_name'
        value = getattr(field, attr)
    return value

def get_filters():
    req = dict(request.args)
    filters = {}
    if 'search' in req:
        search = dict(request.args)['search'][0].replace('?', '')
        if search:
            search = search.split('&')
            for param in search:
                pair = param.split('=')
                if len(pair) > 1:
                    val = pair[1]
                else:
                    val = True
                filters[pair[0]] = val
    filters.update(req)
    return filters

