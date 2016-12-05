from flask import abort, request, current_app
from collections import OrderedDict
from importlib import import_module
from dateutil.relativedelta import relativedelta
from iggybase.admin.models import TableObject
from iggybase.database import db_session
import datetime
import re
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
        if hasattr(table, 'admin_table') and table.admin_table == 1:
            module_model = import_module('iggybase.admin.models')
        else:
            module_model = import_module('iggybase.models')

        # logging.info('after if  ' + table_name)
        table_object = getattr(module_model, to_camel_case(table_name))
    except AttributeError:
        print('Abort' + table_name)
        logging.info('abort ' + table_name)
        abort(403)

    return table_object


def get_table_by_id(table_id):
    session = db_session()
    table = session.query(TableObject).filter_by(id=table_id).first()

    try:
        if hasattr(table, 'admin_table') and table.admin_table == 1:
            module_model = import_module('iggybase.admin.models')
        else:
            module_model = import_module('iggybase.models')

        # logging.info('after if  ' + table_name)
        table_object = getattr(module_model, to_camel_case(table.name))
    except AttributeError:
        print('Abort' + table_id)
        logging.info('abort ' + table_id)
        abort(403)

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
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

def get_last_x_years(x = 10):
    now = datetime.datetime.now()
    years = list(range(now.year, (now.year - x), -1))
    return years

def get_months_dict():
    months = OrderedDict()
    for i in range(1, 13):
        month = datetime.date(1900, i, 1).strftime('%b')
        months[month] = i
    return months

def zero_pad(num, length):
    num_str = str(num)
    num_len = len(num_str)
    if num_len > length:
        return False
    ret = ''
    for x in range(num_len, length):
        ret += '0'
    ret += num_str
    return ret

def html_buttons(buttons):
    html = ''
    for button in buttons:
        if button:
            html += html_button(button)
    return html

def html_button(button):
    html = ('<input value="' + button['value'] + '"' 
    + ' id="' + button['id'] + '"'
    + ' name="' + button['name'] + '"'
    + ' type="' + button['type'] + '"'
    + ' context="' + button['context'] + '"'
    + ' class="' + button['class'] + '"'
    + ' ' + button['special_props'] + '>')
    return html

class DictObject(dict):
    def __init__(self, dict):
        self.__dict__ = dict


def to_snake_case(camel_str):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_last_month():
    return datetime.datetime.now() + relativedelta(months=-1)

def start_and_end_month(year, month):
    from_date = datetime.date(year=year, month=month, day=1)
    to_date = from_date + relativedelta(months=1) - relativedelta(days=1)
    return from_date, to_date
