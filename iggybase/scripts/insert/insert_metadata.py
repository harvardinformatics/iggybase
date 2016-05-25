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
    map = getattr(config, ('base_' + map_name))
    map_by_table = getattr(config, map_name)
    if tbl in map_by_table:
        if is_list:
            map.extend(map_by_table[tbl])
        else:
            map.update(map_by_table[tbl])
    return map

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

def migrate_table(mini_table, thing, new_tbl):
    global iggy_db
    global cli
    print("Table: " + mini_table + " thing: " + thing)
    pks = iggy_db.cursor()
    sql = "select distinct name from " + mini_table + " where thing = '" + thing + "'"
    if 'limit' in cli:
        sql += ' limit ' + cli['limit']
    pks.execute(sql)
    pks_rows = pks.fetchall()
    if 'start' in cli:
        pks_rows = pks_rows[int(cli['start']):]
    print('found rows: ' + str(len(pks_rows)))
    no_skip = False
    if 'no_skip' in cli:
        if cli['no_skip'] == '1':
            no_skip = True
    for row_num, row in enumerate(pks_rows):
        pk = row[0]
        if pk in config.keys_to_skip:
            continue
        print("\t" + str(row_num) + " Working on name: " + pk)
        tbl_name = thing
        print("\t\tMapping data for: " + tbl_name + ' into: ' + new_tbl)
        id_exists = pk_exists(pk, 'name', new_tbl, )
        if id_exists and not no_skip:
            print("\t\tSkipping because " + pk + " already exists: " +
                    str(id_exists))
        else:
            data  = iggy_db.cursor()
            sql = (
                "select * from " + mini_table
                + " where name='" + pk
                + "' and thing='" + tbl_name + "'"
            )
            data.execute(sql)
            data = data.fetchall()
            row_dict = make_dict(data, tbl_name)
            row = do_insert(new_tbl, row_dict)
        print('\tCompleted work on name: ' + pk + "\n\n")
    print('Completed table: ' + mini_table + " thing: " + thing + "\n\n\n\n")

def insert_metadata(table_name, new_name_prefix, role_list):
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
        cols = {'name': table_name, 'new_name_prefix': new_name_prefix}
        table_object_id = insert_row('table_object', cols)
        if table_object_id:
            print("\tTable inserted: " + table_name + " has id: " +
                    str(table_object_id))
        else:
            print("Table NOT inserted, ABORTING: " + table_name)
            return False

    print("\tCheck for TableRoles: " + json.dumps(role_list))
    for role in role_list:
        print("\tCheck for Role: " + str(role))
        table_object_role = select_row('table_object_role', {'table_object_id':
            table_object_id, 'role_id':role})
        if table_object_role:
            table_object_role_id = table_object_role[0]
            print("\tTableRole found, id: " + str(table_object_role_id))
        else:
            print("\tTableRole not found, inserting: " + str(role))
            name, next_num = get_next_name('table_object_role')
            cols = {'table_object_id': table_object_id, 'role_id': role, 'name':
                    name}
            table_object_role_id = insert_row('table_object_role', cols)
            if table_object_role_id:
                print("\tTableRole inserted: " + str(table_object_role_id))
                role_to = select_row('table_object',
                {'name':'table_object_role'})
                role_to_id = role_to[0]
                updated = update_row('table_object', {'id':
                    role_to_id}, {'new_name_id': next_num})
            else:
                print("TableRole NOT inserted: " + str(role))
    print("\tTry to get Fields")
    #fields = select_row(table_name, {}, 1, True)
    fields = show_cols(table_name)
    for i, field in enumerate(fields):
        type_map = {
                'int':1,
                'varchar':2,
                'tinyint':3,
                'datetime':4
        }
        col = field[0]
        print("\t\tTry to insert Field: " + col)
        f_name, f_next_num = get_next_name('field')
        order = i
        data = re.split('[\(\)]', field[1])
        data_type_id = type_map[data[0]]
        length = data[1]
        unique = 0
        pk = 0
        if field[3] == 'PRI':
            pk = 1
        elif field[3] == 'UNI':
            unique = 1
        field_cols = {'table_object_id': table_object_id, 'display_name': col,
                'name': f_name, 'order': order, 'length':length,
                'data_type_id':data_type_id, 'unique':unique, 'primary_key':pk}
        foreign_key_table_object_id = None
        foreign_key_field_id = None
        '''if col == 'organization_id':
            foreign_key_table_object_id = 4
            foreign_key_field_id = 28'''
        field_id = insert_row('field', field_cols)
        print(field_id)
        print(test)

    print(db_tbl)
    print(test)
    #field_ids = insert_rows('field', 'table_object_id',
    #        table_object_ids[0])
    for i, f in enumerate(table_model.__table__.columns):
        field = str(f).split('.')[1]
        print(field)
        field_id = select_row('field',
                {'table_object_id':table_object_id,
                    'field_name': field})
        if not field_id and insert_mode:
            field_id = insert_row('field',
                {'table_object_id':table_object_id,
                    'field_name': field, 'order':i})

    print('Completed model: ' + table_name + "\n\n\n\n")

def get_next_name(table_name):
    table_meta = select_row('table_object', {'name':
    table_name})
    name = table_meta[9]
    num = table_meta[10] + 1
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
                print(val)
                func_name = val.replace('func_', '')
                print(func_name)
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

def select_row(insert_table, criteria, limit = None):
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
'''if 'semantic_source' in cli and 'from_tbl' in cli and 'to_tbl' in cli:
    print(("Semantic Source: " + cli['semantic_source'] + " from_tbl: " +
            cli['from_tbl'] + ' to_tbl: ' + cli['to_tbl']))
else:
    print("Please enter the following required parameters\n\n")
    if 'semantic_source' not in cli:
        cli['semantic_source'] = raw_input("Enter the semantic source table:\n")
    if 'from_tbl' not in cli:
        cli['from_tbl'] = raw_input("Enter the value representing the semantic group for this table:\n")
    if 'to_tbl' not in cli:
        cli['to_tbl'] = raw_input("Enter the name table to migrate to:\n")'''
print(cli)

insert_metadata('unit', 'U', [1, 63])
#migrate_table(cli['semantic_source'], cli['from_tbl'], cli['to_tbl'])
