from flask import abort, request, current_app
from collections import OrderedDict
from importlib import import_module
from dateutil.relativedelta import relativedelta
from iggybase.admin.models import TableObject
from iggybase.database import db_session
import datetime
import re
import logging
import urllib

FACILITY = 0
MODULE = 1
ROUTE = 2
DYNAMIC = 3


def get_column(module, table_name, display_name):
    table_model = get_table(table_name)
    return getattr(table_model, display_name)


def get_table(table, attr = 'name'):
    session = db_session()
    filters = [getattr(TableObject, attr) == table]
    row = session.query(TableObject).filter(*filters).first()

    try:
        if hasattr(row, 'admin_table') and row.admin_table == 1:
            module_model = import_module('iggybase.admin.models')
        else:
            module_model = import_module('iggybase.models')
        table_object = getattr(module_model, to_camel_case(table))

    except AttributeError:
        print('Abort' + table)
        logging.info('abort ' + table)
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
    req = request.args
    filters = {}
    for key, val in req.items():
        # datatables ajax calls will post to search
        if key == 'search':
            if val:
                search = val.replace('?', '').split('&')
                for param in search:
                    pair = param.split('=')
                    if len(pair) > 1:
                        f_val = urllib.parse.unquote(pair[1]).split(',')
                    else:
                        f_val = True
                    f_key = pair[0]
                    filters[f_key] = f_val
        elif key not in ['_']: # datatables passed date with key _
            filters[key] = urllib.parse.unquote(val)
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

def clean_billing_code(code):
    # replace non numbers and dots with dashes
    clean_code = re.sub(r'[^0-9\-]', '', code.replace('.', '-'))
    # replace prefix dash
    clean_code = re.sub(r'^\-+', '', clean_code)
    return clean_code
