import sys
import mysql.connector
from datetime import datetime
import time
import migrate_config as config
from migrate_functions import *
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
    global to_db
    global cli
    if tbl == 'user' and 'email' in row_dict:
        id_exists = pk_exists(row_dict['email'], 'email', tbl)
        if id_exists:
            print("\t\tSkipping because " + row_dict['email'] + " already exists: " +
                    str(id_exists))
            return False

    cols, vals = row_dict.keys(), row_dict.values()
    val_str = make_vals(tbl, cols, vals)
    sql = 'Insert into ' + tbl + ' (`' + '`,`'.join(cols) + '`) values(' + val_str + ')'
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
        insert = to_db.cursor()
        insert.execute(sql)
        to_db.commit()
        if insert.lastrowid:
            row_id = insert.lastrowid
            try:
                print("\t\tSuccessfully inserted row : " + str(row_id) + " sql: " + sql)
            except:
                print("\t\tsql has bad chars")
            ret = row_id
        else:
            try:
                print("\t\tFailed to insert: " + sql)
            except:
                print("\t\tsql has bad chars")
    return ret

def make_vals(tbl, cols, vals):
    val_str = ""
    int_cols = get_map(tbl, 'int_col', True)
    date_cols = get_map(tbl, 'date_col', True)

    for i, col in enumerate(cols):
        if i > 0:
            val_str += ','
        if col in int_cols:
            vals[i] = str(vals[i]).replace(',','')
            val_str += str(vals[i]).replace('$','')
        elif col in date_cols:
            formatted = False
            if '-' in vals[i]:
                date_formats = [ '%Y-%m-%d', '%Y-%m', '%Y-%m-%d %H:%M:%S']
                for date_format in date_formats:
                    try:
                        val_str += '"' + str(datetime.fromtimestamp(time.mktime(time.strptime(vals[i],
                    date_format)))) + '"'
                        formatted = True
                    except:
                        pass
            elif ':' in vals[i]:
                try:
                    date_format = '%b %d %Y %H:%M:%S'
                    val_str += '"' + str(datetime.fromtimestamp(time.mktime(time.strptime(vals[i],
                date_format)))) + '"'
                    formatted = True
                except:
                    val_str += 'Null'

            elif '/' in vals[i]:
                date_formats = ['%m/%d/%y',  '%-m/%d/%y']
                for date_format in date_formats:
                    try:
                        val_str += '"' + str(datetime.fromtimestamp(time.mktime(time.strptime(vals[i],
                        date_format)))) + '"'
                        formatted = True
                    except:
                        pass
            else:
                val_str += '"' + str(datetime.fromtimestamp(int(vals[i]))) + '"'
                formatted = True
            if not formatted:
                val_str += 'Null'
                print('Date could not be formated ' + str(vals[i]))
        else:
            vals[i] = vals[i]
            vals[i].replace("'","\'")
            val_str += '"' + vals[i].replace('"','') + '"'
    return val_str

def pk_exists(pk, name, tbl):
    global to_db
    where = name + "='" + pk.replace("'","\\\'") + "'"
    sql = 'Select id from ' + tbl + " where " + where
    exist = to_db.cursor()
    exist.execute(sql)
    row = exist.fetchone()
    if row:
        row_id = row[0]
    else:
        row_id = None
    return row_id

def migrate_table(mini_table, thing, new_tbl):
    global to_db
    global cli
    print("Table: " + mini_table + " thing: " + thing)
    pks = to_db.cursor()
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
            data  = to_db.cursor()
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

from_db = get_connection(
    config.db['from']['user'],
    config.db['from']['password'],
    config.db['from']['host'],
    config.db['from']['database']
)

to_db = get_connection(
    config.db['to']['user'],
    config.db['to']['password'],
    config.db['to']['host'],
    config.db['to']['database']
)

args = sys.argv[1:]
for arg in args:
    pair = arg.split('=',1)
    name = pair[0]
    val = True
    if len(pair) > 1:
        val = pair[1]
    cli[name.replace('--','')] = val
if 'semantic_source' in cli and 'from_tbl' in cli and 'to_tbl' in cli:
    print(("Semantic Source: " + cli['semantic_source'] + " from_tbl: " +
            cli['from_tbl'] + ' to_tbl: ' + cli['to_tbl']))
else:
    print("Please enter the following required parameters\n\n")
    if 'semantic_source' not in cli:
        cli['semantic_source'] = raw_input("Enter the semantic source table:\n")
    if 'from_tbl' not in cli:
        cli['from_tbl'] = raw_input("Enter the value representing the semantic group for this table:\n")
    if 'to_tbl' not in cli:
        cli['to_tbl'] = raw_input("Enter the name table to migrate to:\n")
print(cli)

migrate_table(cli['semantic_source'], cli['from_tbl'], cli['to_tbl'])
