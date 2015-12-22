import sys
import mysql.connector
from datetime import datetime
import time
import config

"""
script for migrating data from minilims to iggybase

- use one table at a time
- set up maps for any special columns
- call migrate_table with table name at the bottom

CLI options include
--insert_mode : will actually do the inserts
--limit: limit to rows selected
--start: of those selected start at this #

exp use:
python migrate.py --insert_mode --limit=2 --start=1
(this will select two rows but only work on the second and will perform insert)
"""
class Column:
    name, thing, property, value = range(0,4)

cli = {}

# col name old to new, or function which will produce new col, none means skip
base_col_map = {
    'date_modified': 'last_modified',
    'deleted': 'active',
    'notes': 'func_insert_long_text',
    'note_id':'func_insert_long_text',
    'group_member': 'func_get_fk',
    'group': 'func_get_fk'

}
# by table
col_maps = {
    'group':{
        'group_member': None,
        'group': None, #organization tbl exception
        'pi': None
    },
    'group_member':{
        'username': 'name',
        'full_name': 'func_split_name',
        'admin': None,
        'phone': None,
        'street_address': None,
        'city': None,
        'state': None,
        'zip': None,
        'institution': None
    },
    'oligo':{
        'sequence':'func_insert_long_text',
        'status':'func_get_fk'
    },
    'strain':{
        'background':'func_insert_long_text',
        'comments':'func_insert_long_text'
    },
    'plasmid':{
        'mod_notes':'func_insert_long_text',
        'constr_notes':'func_insert_long_text',
        'insert_notes':'func_insert_long_text',
        'vector_notes':'func_insert_long_text',
        'publications':'func_insert_long_text',
        'purpose':'func_insert_long_text'
    },
    'fragment':{
        'plasmid':'func_get_fk',
        'description':'func_insert_long_text'
    },
    'genotype':{
        'strain':'func_get_fk',
        'genotype_id':None
    },
    'oligo_fragment':{
        'oligo':'func_get_fk',
        'description':'func_insert_long_text'
    },
    'oligo_batch':{
        'oligo':'func_get_fk',
        'orderer':'func_get_fk',
        'receiver':'func_get_fk',
        'requester':'func_get_fk',
        'canceler':'func_get_fk',
        'order_notes':'func_insert_long_text',
        'cancel_notes':'func_insert_long_text',
        'request_notes':'func_insert_long_text',
        'oligo_batch_id': None,
        'receiver_date': 'receive_date'
    }
}

# adds columns to the table
base_add_cols = {
        'active': 1,
        'organization_id':8
}
# by table
add_cols_map = {
        'group_member':{
            'func_user_org': 'Murray'
        }
}

# int cols
base_int_col_map = ['active', 'organization_id', 'note_id', 'user_id']
# by table
int_col_map = {
        'oligo': [
            'sequence', 'status'
        ],
        'strain': [
            'background', 'comments'
        ],
        'plasmid': [
            'mod_notes', 'constr_notes', 'insert_notes', 'vector_notes',
            'publications', 'purpose'
        ],
        'fragment': [
            'plasmid_id', 'description'
        ],
        'genotype': [
            'strain_id'
        ],
        'oligo_fragment':[
            'oligo_id', 'description'
        ],
        'oligo_order':[
            'oligo_id', 'orderer',
            'receiver','canceler','order_notes','cancel_notes',
            'requester','request_notes'
        ]
}

# date cols
base_date_col_map = ['last_modified', 'date_created', 'entry_date']
# by table
date_col_map = {
    'oligo_order': [
        'request_date','order_date','cancel_date','receive_date'
    ]
}

# fk field to table
fk_tbl_map = {
        'group_member': 'user',
        'group': 'organization',
        'status': 'status',
        'plasmid': 'plasmid',
        'strain':'strain',
        'oligo':'oligo',
        'requester':'user',
        'orderer':'user',
        'receiver':'user',
        'canceler':'user'
}

# use to just skip some troublesome rows
keys_to_skip = ['Weinstein_Bryan', 'Bryan Weinstein', 'Bryan_Weinstein']

def get_connection(user, password, host, database):
    db = mysql.connector.connect(
            user = user,
            password = password,
            host = host,
            database = database
    )
    return db

def make_dict(data, tbl):
    tbl = tbl.lower()
    col_map = base_col_map
    if tbl in col_maps:
        col_map.update(col_maps[tbl])

    add_cols = base_add_cols
    if tbl in add_cols_map:
        add_cols.update(add_cols_map[tbl])
    for col, val in add_cols.items():
        data.append(["", tbl, col, val])
    row_dict = {}
    for row in data:
        col = row[Column.property].lower()
        val = row[Column.value]
        if val: # don't both inserting nones
            # skip or map columns
            if col == tbl:# if this is the table then skip, dup of name
                continue
            elif col in col_map:
                if col_map[col]:
                    new_col = col_map[col]

                else: # if the new_col is null then skip
                    continue
            else:
                new_col = col
            # execute any funcs
            if 'func_' in new_col:
                func_name = new_col.replace('func_', '')
                if func_name in globals():
                    new_dict =  globals()[func_name](col, val)
                else:
                    print('Error, no function defined')
                    sys.exit(1)
            else:
                new_dict = {new_col: val}
            row_dict.update(new_dict)
    print("\t\t" + str(row_dict))
    return row_dict

def do_insert(tbl, row_dict):
    global iggy_db
    global cli
    cols, vals = row_dict.keys(), row_dict.values()
    val_str = make_vals(tbl, cols, vals)
    sql = 'Insert into ' + tbl + ' (' + ','.join(cols) + ') values(' + val_str + ')'
    print("\t\t" + sql)
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
            print("\t\tSuccessfully inserted row : " + str(row_id) + " sql: " + sql)
            ret = row_id
        else:
            print("\t\tFailed to insert: " + sql)
    return ret

def make_vals(tbl, cols, vals):
    val_str = ""
    int_cols = base_int_col_map
    if tbl in int_col_map:
        int_cols.extend(int_col_map[tbl])
    date_cols = base_date_col_map
    if tbl in date_col_map:
        date_cols.extend(date_col_map[tbl])
    for i, col in enumerate(cols):
        if i > 0:
            val_str += ','
        if col in int_cols:
            val_str += str(vals[i])
        elif col in date_cols:
            if '-' in vals[i]:
                date_format = '%Y-%m-%d'
                val_str += '"' + str(datetime.fromtimestamp(time.mktime(time.strptime(vals[i],
                date_format)))) + '"'
            elif '/' in vals[i]:
                date_format = '%m/%d/%y'
                val_str += '"' + str(datetime.fromtimestamp(time.mktime(time.strptime(vals[i],
                date_format)))) + '"'
            else:
                val_str += '"' + str(datetime.fromtimestamp(int(vals[i]))) + '"'
        else:
            val_str += '"' + vals[i].replace('"','') + '"'
    return val_str

def pk_exists(pk, tbl):
    global iggy_db
    where = "name='" + pk + "'"
    if tbl == 'user':
        names =  split_name('name', pk)
        where = ''
        if names['first_name']:
            where += "first_name='" + names['first_name'] + "'"
        if names['last_name']:
            where += "and last_name='" + names['last_name'] + "'"
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
    global mini_db
    global cli
    print("Table: " + mini_table + " thing: " + thing)
    pks = mini_db.cursor()
    sql = "select distinct name from " + mini_table + " where thing = '" + thing + "'"
    if 'limit' in cli:
        sql += ' limit ' + cli['limit']
    pks.execute(sql)
    pks_rows = pks.fetchall()
    if 'start' in cli:
        pks_rows = pks_rows[int(cli['start']):]
    for row_num, row in enumerate(pks_rows):
        pk = row[0]
        if pk in keys_to_skip:
            continue
        print("\t" + str(row_num) + " Working on name: " + pk)
        tbl_name = thing
        print("\t\tMapping data for: " + tbl_name + ' into: ' + new_tbl)
        id_exists = pk_exists(pk, new_tbl)
        if id_exists:
            print("\t\tSkipping because " + pk + " already exists: " +
                    str(id_exists))
        else:
            data  = mini_db.cursor()
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

""" column specific functions
"""
def split_name(col, val):
    if '_' in val:
        names = val.split('_', 1)
        first, last = names[0], names[1]
    else:
        first = val
        last = ''
    new_dict = {'first_name': first, 'last_name': last}
    return new_dict

def get_fk(col, val):
    new_dict = {}
    if col in fk_tbl_map:
        if col in fk_tbl_map:
            new_col = fk_tbl_map[col]
        else:
            new_col = col
        fk_id = pk_exists(val, new_col)
        if fk_id:
            if new_col in ['status']:
                new_dict = {new_col: fk_id}
            elif col in ['canceler','receiver','requester','orderer']:
                new_dict = {col: fk_id}
            else:
                new_dict = {(new_col + '_id'): fk_id}
    return new_dict

def get_status(col, val):
    new_dict = {}
    if fk_tbl_map[col]:
        new_tbl = fk_tbl_map[col]
        fk_id = pk_exists(val, new_tbl)
        if fk_id:
            new_dict = {(new_tbl + '_id'): fk_id}
    return new_dict

def insert_long_text(col, val):
    global iggy_db
    if col == 'notes':
        col_name = 'note_id'
    else:
        col_name = col
    # check if the long_text exists
    sql = 'select id from long_text where long_text = "' + val.replace('"','') + '"'
    long_text = iggy_db.cursor()
    long_text.execute(sql)
    long_text = long_text.fetchone()
    if long_text and long_text[0]:
        return {col_name: long_text[0]}

    sql = 'select max(id) from long_text'
    max_id = iggy_db.cursor()
    max_id.execute(sql)
    max_id = max_id.fetchone()
    if max_id:
        max_id = max_id[0]
    if not max_id:
        max_id = 1
    else:
        max_id = max_id + 1
    # TODO: we need to fix name to not have constant 4 zeros
    if len(str(max_id)) == 1:
        name = 'LT00000' + str(max_id)
    else:
        name = 'LT0000' + str(max_id)
    sql = (
        'insert into long_text (name, active, organization_id, long_text)'
        + ' values("' + name + '", 1, 8, "' + val.replace('"','') + '")'
    )
    print("\t\t\t" + sql)
    note = iggy_db.cursor()
    note.execute(sql)
    iggy_db.commit()
    fk_id = note.lastrowid
    new_dict = {col_name: fk_id}
    return new_dict

def user_org(col, val):
    org_id = pk_exists(val, 'organization')
    return {'organization_id': org_id}

mini_db = get_connection(
    config.RC_Development.PROJECT,
    config.RC_Development.DB_KEY,
    config.RC_Development.DB_ADDRESS,
    'murraylabweb_minilims'
)
iggy_db = get_connection(
    config.RC_Development.PROJECT,
    config.RC_Development.DB_KEY,
    config.RC_Development.DB_ADDRESS,
    config.RC_Development.DATA_DB_NAME
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


# migrate_table('semantic_data', 'Group', 'organization')
# migrate_table('semantic_data', 'Group_Member', 'user')
# migrate_table('semantic_data', 'Oligo', 'oligo')
# migrate_table('semantic_data', 'Strain', 'strain')
# migrate_table('semantic_data', 'Plasmid', 'plasmid')
# migrate_table('semantic_data', 'Fragment', 'fragment')
# migrate_table('semantic_data', 'Genotype', 'genotype')
# migrate_table('semantic_data', 'Oligo_Fragment', 'oligo_fragment')
migrate_table('semantic_data', 'Oligo_Batch', 'oligo_order')

