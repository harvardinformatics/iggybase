from flask import abort, request
from importlib import import_module
from iggybase.admin.models import TableObject
from iggybase.database import db_session
import logging

FACILITY = 0
MODULE = 1
ROUTE = 2
DYNAMIC = 3


def get_column(module, table_name, display_name):
    table_model = get_table(table_name)
    return getattr(table_model, display_name)


def get_table(table_name):
    session = db_session()
    table = session.query(TableObject).filter_by(name=table_name).first()

    try:
        if table.admin_table == 1:
            module_model = import_module('iggybase.admin.models')
        else:
            module_model = import_module('iggybase.models')

        # logging.info('after if  ' + table_name)
        table_object = getattr(module_model, to_camel_case(table_name))
    except AttributeError:
        logging.info('abort ' + table_name)
        abort(403)
    finally:
        session.commit()

    return table_object


def get_func(module_name, func_name):
    """Return function from it's name.
    Returns None if unsuccessful.
    """
    if not module_name or not func_name:
        return None
    try:
        module = import_module(module_name)
        func = getattr(module, func_name, None)
        return func
    except:
        logging.info('could not import module_name ' + module_name)
        func = None

    return func  # Possible None


def get_field_attr(field, table_query_field, attr):
    if table_query_field and getattr(table_query_field, attr):
        value = getattr(table_query_field, attr)
    else:
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


def get_path(part):
    path = request.path.strip('/')
    path = path.split('/')
    return path[part]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in application.config.ALLOWED_EXTENSIONS


class DictObject(dict):
    def __init__(self, dict):
        self.__dict__ = dict
