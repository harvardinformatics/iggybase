from flask import abort, request, g
from importlib import import_module
from iggybase.tablefactory import TableFactory
from iggybase.admin.models import TableObject
from iggybase.database import db_session
from iggybase.auth.role_access_control import RoleAccessControl
import logging

def get_role_access_control():
    if 'role_access' not in g:
        g.role_access = RoleAccessControl()
    return g.role_access

def get_column(module, table_name, field_name):
    table_model = get_table(table_name)
    return getattr(table_model, field_name)

def get_table(table_name):
    session = db_session()
    table = session.query(TableObject).filter_by(name=table_name).first()

    try:
        if table.admin_table == 1:
            module_model = import_module('iggybase.admin.models')
        else:
            module_model = import_module('iggybase.models')
        table_object = getattr(module_model, TableFactory.to_camel_case(table_name))
    except AttributeError:
        logging.info('abort ' + table_name)
        abort(403)
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

def to_camel_case(snake_str):
    components = snake_str.split('_')

    return "".join(x.title() for x in components)

class DictObject(dict):
    def __init__(self, dict):
        self.__dict__ = dict
