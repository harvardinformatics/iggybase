import sys, json
import mysql.connector
from datetime import datetime
import time
import insert_config as config
import re

"""
script for migrating data from semantic to relational tables

- use one table at a time, table name taken from cli
- set up maps for any special columns in migrate_config.py
- set up any custom functions in migrate_functions.py

CLI requirements include (raw input requested if not entered):
    --semantic_source: the semantic source table
    --from_tbl: the semantic source table
    --to_tbl: the semantic source table
CLI options include
    --insert_mode: will actually do the inserts
    --limit: limit to rows selected
    --start: of those selected start at this #
    --no_skip: format the insert even if pk exists

exp use:
python migrate.py --insert_mode --limit=2 --start=1
(this will select two rows but only work on the second and will perform insert)
"""
cli = {}

def get_connection(user, password, host, database):
    db = mysql.connector.connect(
            user = user,
            password = password,
            host = host,
            database = database
    )
    return db

def get_map(tbl, prefix, is_list = False):
    map_name = prefix + '_map'
    base_map_name = 'base_' + map_name
    base_map = getattr(config, base_map_name)
    map_by_table = getattr(config, map_name)
    if is_list:
        ret_map = []
        ret_map.extend(base_map)
    else:
        ret_map = {}
        ret_map.update(base_map)
    if tbl in map_by_table:
        if is_list:
            ret_map.extend(map_by_table[tbl])
        else:
            ret_map.update(map_by_table[tbl])
    return ret_map

def make_dict(data, tbl):
    col_name_map = get_map(tbl, 'col_name')
    tbl = tbl.lower()
    col_value_map = get_map(tbl, 'col_value')
    add_cols = get_map(tbl, 'add_cols')

    for col, val in add_cols.items():
        data.append(["", "", tbl, col, val])
    row_dict = {}

    for row in data:
        col = row[config.semantic_col_map['col_name']].lower()
        col = col.replace(" ",'_')
        col = re.sub('\s+','', col)
        val = row[config.semantic_col_map['value']]
        if val: # don't bother inserting nones
            # skip or map columns
            if col == tbl:# if this is the table then skip, dup of name
                continue
            elif col in col_name_map:
                if col_name_map[col]:
                    new_col = col_name_map[col]
                else: # if the new_col is null then skip
                    continue
            else:
                new_col = col
            # execute any funcs
            if col in col_value_map:
                value_map = col_value_map[col]
                if 'func_' in value_map:
                    func_name = value_map.replace('func_', '')
                    if func_name in globals():
                        new_dict =  globals()[func_name](col, val, col_name_map)
                    else:
                        print('Error, no function defined: ' + func_name)
                        sys.exit(1)
                else:
                    new_dict = {new_col: value_map}
            else:
                new_dict = {new_col: val}
            row_dict.update(new_dict)
    print("\t\t" + str(row_dict))
    return row_dict

def do_insert(tbl, row_dict):
    global iggy_db
    global cli
    if tbl == 'user' and 'email' in row_dict:
        id_exists = pk_exists(row_dict['email'], 'email', tbl)
        if id_exists:
            print("\t\tSkipping because " + row_dict['email'] + " already exists: " +
                    str(id_exists))
            return False

    val_str = make_vals(tbl, row_dict)
    sql = 'Insert into ' + tbl + ' (`' + '`,`'.join(list(row_dict.keys())) + '`) values(' + val_str + ')'
    try:
        print("\t\t" + sql)
    except:
        print("\t\t" + 'sql has bad characters')
    if 'insert_mode' in cli:
        insert_mode = True
    else:
        insert_mode = False
        print("\t\tNo insert: use opt --insert_mode to actually insert")

    ret = False
    if insert_mode:
        insert = iggy_db.cursor()
        insert.execute(sql)
        iggy_db.commit()

        if insert.lastrowid:
            row_id = insert.lastrowid
            try:
                print("\t\tSuccessfully inserted row : " + str(row_id))
            except:
                print("\t\tsql has bad chars")
            ret = row_id
        else:
            try:
                print("\t\tFailed to insert: " + sql)
            except:
                print("\t\tsql has bad chars")
    return ret

def make_vals(tbl, cols):
    val_str = ""
    int_cols = get_map(tbl, 'int_col', True)
    date_cols = get_map(tbl, 'date_col', True)
    i = 0
    for col, val in cols.items():
        if i > 0:
            val_str += ','
        if col in int_cols:
            val = str(val).replace(',','')
            val_str += str(val).replace('$','')
        elif col in date_cols:
            formatted = False
            if '-' in val:
                date_formats = [ '%Y-%m-%d', '%Y-%m', '%Y-%m-%d %H:%M:%S']
                for date_format in date_formats:
                    try:
                        val_str += '"' + str(datetime.fromtimestamp(time.mktime(time.strptime(val,
                    date_format)))) + '"'
                        formatted = True
                    except:
                        pass
            elif ':' in val:
                try:
                    date_format = '%b %d %Y %H:%M:%S'
                    val_str += '"' + str(datetime.fromtimestamp(time.mktime(time.strptime(val,
                date_format)))) + '"'
                    formatted = True
                except:
                    val_str += 'Null'

            elif '/' in val:
                date_formats = ['%m/%d/%y',  '%-m/%d/%y']
                for date_format in date_formats:
                    try:
                        val_str += '"' + str(datetime.fromtimestamp(time.mktime(time.strptime(val,
                        date_format)))) + '"'
                        formatted = True
                    except:
                        pass
            else:
                val_str += '"' + str(datetime.fromtimestamp(int(val))) + '"'
                formatted = True
            if not formatted:
                val_str += 'Null'
                print('Date could not be formated ' + str(val))
        else:
            val.replace("'","\'")
            val_str += '"' + val.replace('"','') + '"'
        i += 1
    return val_str

def pk_exists(pk, name, tbl):
    global iggy_db
    where = name + "='" + pk.replace("'","\\\'") + "'"
    sql = 'Select id from ' + tbl + " where " + where
    exist = iggy_db.cursor()
    exist.execute(sql)
    row = exist.fetchone()
    if row:
        row_id = row[0]
    else:
        row_id = None
    return row_id

def insert_metadata(table_name, new_name_prefix, role_list, order):
    global iggy_db
    global cli
    print("Starting on Table: " + table_name + ' and role_list: ' +
            json.dumps(role_list))
    print("\tCheck for Table: " + table_name)
    table_object = select_row('table_object', {'name': table_name})
    if table_object:
        table_object_id = table_object[0]
        print("\tTable found, id: " + str(table_object_id))
    else:
        print("\tTable not found, inserting: " + table_name)
        cols = {'name': table_name, 'new_name_prefix': new_name_prefix,
                'order':order}
        table_object_id = insert_row('table_object', cols)
        if table_object_id:
            print("\tTable inserted: " + table_name + " has id: " +
                    str(table_object_id))
        else:
            print("Table NOT inserted, ABORTING: " + table_name)
            return False
    add_roles('table_object', table_object_id, role_list)
    print("\tTry to get Fields")
    fields = show_cols(table_name)
    for i, field in enumerate(fields):
        if field:
            col = field[0]
            print("\t\tCheck Field: " + col)
            field_row = select_row('field', {'display_name': col,
                'table_object_id':table_object_id})
            if field_row:
                field_id = field_row[0]
                print("\t\tField found: " + str(field_id))
                add_roles('field', field_id, role_list)
            else:
                print("\t\tField not found, inserting")
                type_map = {
                        'int':1,
                        'varchar':2,
                        'tinyint':3,
                        'datetime':4,
                        'decimal':9,
                        'float':10
                }
                f_name, f_next_num = get_next_name('field')
                order = i
                data = re.split('[\(\)]', field[1])
                data_type_id = type_map[data[0]]
                unique = 0
                pk = 0
                if field[3] == 'PRI':
                    pk = 1
                elif field[3] == 'UNI':
                    unique = 1
                field_cols = {'table_object_id': table_object_id, 'display_name': col,
                        'name': f_name, 'order': order,
                        'data_type_id':data_type_id, 'unique':unique, 'primary_key':pk}

                if data_type_id != 4 and 1 in data:
                    field_cols['length'] = data[1]
                foreign_key_table_object_id = None
                foreign_key_field_id = None
                if '_id' in col:
                    fk_tbl = col.split('_id')[0]
                    fk_table_object = select_row('table_object', {'name': fk_tbl})
                    if fk_table_object:
                        foreign_key_table_object_id = fk_table_object[0]
                        fk_field = select_row('field', {'table_object_id':
                            foreign_key_table_object_id, 'display_name':'id'})
                        if fk_field:
                            foreign_key_field_id = fk_field[0]
                if foreign_key_table_object_id:
                    field_cols['foreign_key_table_object_id'] = foreign_key_table_object_id
                if foreign_key_field_id:
                    field_cols['foreign_key_field_id'] = foreign_key_field_id
                field_id = insert_row('field', field_cols)
                if field_id:
                    print("\tField inserted: " + str(field_id))
                    field_to = select_row('table_object',
                    {'name':'field'})
                    field_to_id = field_to[0]
                    updated = update_row('table_object', {'id':
                        field_to_id}, {'new_name_id': f_next_num})
                    add_roles('field', field_id, role_list)
                else:
                    print("\tField NOT inserted: " + str(col))

    print("Completed Table: " + table_name + "\n\n\n")

def add_roles(tbl_name, tbl_id, role_list):
    print("\tCheck for " + tbl_name + "Role: " + json.dumps(role_list))
    for role in role_list:
        print("\tCheck for Role: " + str(role))
        table_object_role = select_row((tbl_name + '_role'), {(tbl_name + '_id'):
            tbl_id, 'role_id':role})
        if table_object_role:
            table_object_role_id = table_object_role[0]
            print("\t" + tbl_name + "Role found, id: " + str(table_object_role_id))
        else:
            print("\t" + tbl_name + "Role not found, inserting: " + str(role))
            name, next_num = get_next_name((tbl_name + '_role'))
            cols = {(tbl_name + '_id'): tbl_id, 'role_id': role, 'name':
                    name}
            table_object_role_id = insert_row((tbl_name + '_role'), cols)
            if table_object_role_id:
                print("\t" + tbl_name + "Role inserted: " + str(table_object_role_id))
                role_to = select_row('table_object',
                {'name':(tbl_name + '_role')})
                role_to_id = role_to[0]
                updated = update_row('table_object', {'id':
                    role_to_id}, {'new_name_id': next_num})
            else:
                print(tbl_name + "Role NOT inserted: " + str(role))

def get_next_name(table_name):
    table_meta = select_row('table_object', {'name':
    table_name})
    name = table_meta[9]
    num = table_meta[10]
    next_num = num + 1
    dig = table_meta[11] - len(str(num))
    for i in range(0,dig):
        name += '0'
    name += str(num)
    return name, next_num

def insert_row(tbl, cols):
    col_val_map = get_map(tbl, 'col_value')
    cols.update(col_val_map)
    if cols:
        fields = {}
        sql = 'insert into ' + tbl
        for key, val in cols.items():
            if 'func_' in str(val):
                func_name = val.replace('func_', '')
                if func_name in globals():
                    criteria['insert_table'] = insert_table
                    fields[key] =  globals()[func_name](key, criteria)
                else:
                    print('Error, no function ' + func_name + ' defined')
                    sys.exit(1)
            else:
                fields[key] = val
        id = do_insert(tbl, fields)
        return id

def update_row(tbl, criteria, cols):
    global cli
    if 'insert_mode' in cli:
        pks = iggy_db.cursor()
        sql = "update " + tbl
        int_cols = get_map(tbl, 'int_col', True)
        for name, val in cols.items():
            if name in int_cols:
                sql += ' set ' + name + ' = ' + str(val)
            else:
                sql += ' set ' + name + ' = "' + val + '"'
        sql += ' where '
        for key, crit in criteria.items():
            sql += key + ' = ' + str(crit)
        print("\t\t" + sql)
        pks.execute(sql)
        iggy_db.commit()

def show_cols(tbl):
    pks = iggy_db.cursor()
    sql = "show columns from " + tbl
    print("\t\t" + sql)
    pks.execute(sql)
    pks_row = pks.fetchall()
    print(pks_row)
    return pks_row

# TODO: compare with pk_exists
def select_row(insert_table, criteria, limit = 1):
    pks = iggy_db.cursor()
    sql = "select * from " + insert_table
    wheres = []
    for key, val in criteria.items():
        if '_id' in key or key == 'id':
            wheres.append(key + " = " + str(val))
        else:
            wheres.append(key + " like '" + val + "'")
    if wheres:
        sql += ' where ' + ' and '.join(wheres)
    if limit:
        sql += ' limit 1'
    print("\t\t" + sql)
    pks.execute(sql)
    pks_row = pks.fetchone()
    return pks_row



iggy_db = get_connection(
    config.db['from']['user'],
    config.db['from']['password'],
    config.db['from']['host'],
    config.db['from']['database']
)

args = sys.argv[1:]
for arg in args:
    pair = arg.split('=',1)
    name = pair[0]
    val = True
    if len(pair) > 1:
        val = pair[1]
    cli[name.replace('--','')] = val
print(cli)

#insert_metadata('unit', 'U', [1, 63])
#insert_metadata('reagent', 'R', [1, 63])
#insert_metadata('illumina_adapter', 'R', [1, 63])
#insert_metadata('sequencing_price', 'SP', [1, 63])
#insert_metadata('project', 'PR', [1, 63])
#insert_metadata('invoice_template', 'IT', [1, 63])
#insert_metadata('machine', 'MN', [1, 63])
#insert_metadata('purchase_order', 'PO', [1, 63])
#insert_metadata('line_item', 'LI', [1, 63])
#insert_metadata('illumina_bclconversion_analysis', 'BCL', [1, 63])
#insert_metadata('illumina_run', 'IR', [1, 63])
#insert_metadata('sample', 'SA', [1, 63])
#insert_metadata('sample_sheet', 'SS', [1, 63])
#insert_metadata('reagent_request', 'RR', [1, 63], 31)
#insert_metadata('illumina_flowcell', 'IF', [1, 63], 32)
#insert_metadata('invoice', 'IV', [1, 63], 33)
#insert_metadata('charge_method_type', 'CMT', [1, 63], 34)
#insert_metadata('charge_method', 'CM', [1, 63], 35)
#insert_metadata('invoice_item', 'II', [1, 63], 36)
#insert_metadata('invoice_template', 'IT', [1, 63], 37)
#insert_metadata('order_charge_method', 'OCM', [1, 63], 38)
#insert_metadata('price_category', 'PC', [1, 63], 39)
#insert_metadata('price_list', 'PL', [1, 63], 40)
#insert_metadata('sample_sheet_item', 'SI', [1, 63], 41)
#insert_metadata('select_list', 'SL', [1, 63], 42)
#insert_metadata('select_list_item', 'SLI', [1, 63], 43)
#insert_metadata('transaction_type', 'TT', [1, 63], 45)
insert_metadata('price_list', 'PL', [1, 63], 41)
#insert_metadata('price_item', 'PI', [1, 63], 40)
#insert_metadata('price_type', 'PT', [1, 63], 39)
