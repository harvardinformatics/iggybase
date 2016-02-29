import sys
import mysql.connector
from datetime import datetime
import time
import config
import re

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
    name, thing, property, value = range(1,5)

max_id = None

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
    'reagent':{
        'status':'func_get_active'
        },
    'invoice':{
        'line_item':'func_get_fk',
        'lab_admin_name':'func_get_fk',
        'lab_admin_email':None
        },
    'line_item':{
        'lab_admin_name':'func_get_fk',
        'billable_item':'func_get_fk',
        'quantity':'func_make_numeric',
        'sequencing_price':'func_get_fk',
        'lab_admin_email':None,
        'billable_item_type':None,
        'expense_code_percentage':None,
        'purchase_order':None,
        'reagent':None
        },
    'illumina_flowcell':{
        'illumina_run':'func_get_fk',
        'directory_location':None,
        'directory_size':None,
        'notes':None,
        'read_length':None,
        'library_type':None
        },
    'sample_sheet':{
        'illumina_flowcell':'func_get_fk',
        'illumina_run':'func_get_fk',
        'machine':'func_get_fk',
        'experiment_name':'func_get_fk',
        'experimentname':'func_get_fk',
        'investigatorname':'func_get_fk',
        'investigator_name':'func_get_fk',
        'adapter':'adapter_1',
        'adapterread2':'adapter_2',
        'iemfileversion':'iemfile_version'
        },
    'illumina_run':{
        'submission':'func_get_fk',
        'machine':'func_get_fk',
        'illumina_bclconversion_analysis':'func_get_fk',
        'read_1_index':'func_get_bool',
        'read_2_index':'func_get_bool',
        'read_3_index':'func_get_bool',
        'read_4_index':'func_get_bool',
        'illumina_flowcell':None,
        'count':None,
        'bustardsummary.xml':None,
        'runname':None,
        'yield':None,
        'clusters':None,
        'passing_clusters':None,
        'passing_clusters_percent':None,
        'kb_sequenced':None,
        'call_cycle':None,
        'image_cycle':None,
        'num_cycles':None,
        'percent_called':None,
        'percent_imaged':None,
        'percent_scored':None,
        'run_started':None,
        'score_cycle':None,
        'demultiplex_stats.htm':None,
        'ivc_html':None,
        'all_html':None,
        'notes':None,
        'run_sample_sheet':None
        },
    'illumina_bclconversion_analysis':{
        'illumina_run':None,
        'submission':'func_get_fk',
        'run_directory':None,
        'illumina_lane':None,
        'timestamp':None,
        'data_directory':None,
        'command':'func_insert_long_text'
        },
    'sample_sheet_item':{
        'operator':'func_get_fk',
        'project':'func_get_fk',
        'submission':'func_get_fk',
        'sample_name':'func_get_fk',
        'sample_sheet':'func_get_fk',
        'recipe':'func_make_numeric',
        'lane':'func_make_numeric',
        'control':'func_get_bool',
        'i5_index_id':None,
        'i7_index_id':None,
        'index2':None,
        'sample_id':None,
        'sample_project':None,
        'sample_plate':None,
        'sample_well':None,
        },
    'sample':{
        'bioanlyzer_performed':'func_get_bool',
        'qpcr_performed':'func_get_bool',
        'qubit_performed':'func_get_bool',
        'volume_(ul)':'func_make_numeric',
        'fragment_size_(bp)':'fragment_size',
        'multiplex_sample_-_lane_id':'multiplex_sample_lane_id',
        'read_length':'func_make_numeric',
        'concentration':'func_make_numeric',
        'submission':'func_get_fk',
        'low_diversity_library':'func_get_bool',
        'is_dual_indexed':'func_get_bool',
        'project':'func_get_fk',
        'index_sequence':'func_insert_long_text',
        'bioanalyzer_service_requested':'func_get_bool',
        'date_finished':None,
        'date_received':None,
        'primer_type':None,
        'use_index':None,
        'bioanalyzer_status':None,
        'bioanalyzer_file':None,
        'notes':None
        },
    'submission': {
        'submitter_name':'func_get_fk',
        'comments':'func_insert_long_text',
        'purchase_order_file':None,
        'purchase_order_number':None,
        'destination_directory':None,
        'run_type':None,
        'expense_code_2':None,
        'expense_code_3':None,
        'phone':None,
        'email':None,
        'pi':None
        },
    'reagent_request':{
        'expense_code_percentage_1': None,
        'submitter_name':'func_get_fk',
        'reagent':'func_get_fk',
        'expense_code_1':'expense_code',
        'purchase_order_number':None,
        'purchase_order_file':None,
        'notes':'func_insert_long_text',
        'quantity':'func_make_numeric'
        },
    'purchase_order':{
        'status':'func_get_active',
        'pi':'func_get_fk',
        'owner':'func_get_fk',
        'owner_institution':'func_get_fk'
        #'billing_address':None,
        #'owner_address': None
        },
    'sequencing_price':{
        'single_lane/full_flowcell':'lane_type',
        'paired_end':'func_get_bool'
        },
    'group':{
        'group_member': None,
        'group': None, #organization tbl exception
        'pi': None,
        'department': 'func_get_fk',
        'type': None,
        'lab_admin': None,
        'sequencing_notes': None,
        'web_page': None,
        'location': None
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
        'institution': None,
        'affiliation':None,
        'picture': None,
        'notes':None,
        'state': None,
        'institution_type': None,
        'user_id': None,
        'postal_code': None,
        'title': None,
        'department': None
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
        'organization_id':84
}
# by table
add_cols_map = {
        'group':{
            'organization_id':1
        },
        'group_member':{
            'func_user_org':'func_user_org'
        }
}

# int cols
base_int_col_map = ['active', 'organization_id', 'note_id', 'user_id',
'department_id', 'machine_id', 'project_id', 'submission_id', 'sample_id',
'illumina_bclconversion_analysis_id','illumina_run_id','illumina_flowcell_id',
'sample_sheet_id', 'reagent_request_id', 'sequencing_price_id']
# by table
int_col_map = {
        'reagent_request':[
            'submitter',
            'reagent_id',
            'quantity',
            'notes'
            ],
        'invoice':[
            'line_item_id',
            'lab_admin',
            'total_cost',
            'total_credit'
            ],
        'line_item':[
            'lab_admin',
            'cost',
            'quantity'
            ],
        'sample_sheet':[
            'iemfile_version',
            'read_length_1',
            'investigator',
            'read_length_2',

            ],
        'illumina_flowcell':[
            'swath_count',
            'surface_count',
            'lane_count',
            'tile_count'
            ],
        'illumina_run':[
            'read_1_cycles',
            'read_2_cycles',
            'read_3_cycles',
            'read_4_cycles',
            'read_1_index',
            'read_2_index',
            'read_3_index',
            'read_4_index'
            ],
        'illumina_bclconversion_analysis':[
            'job_id',
            'command'
            ],
        'sample_sheet_item':[
            'control',
            'operator',
            'lane',
            'recipe'
            ],
        'sample':[
            'read_length',
            'bioanlyzer_performed',
            'qpcr_performed',
            'qubit_performed',
            'volume',
            'concentration',
            'low_diversity_library',
            'is_dual_indexed',
            'index_sequence',
            'bioanalyzer_service_requested',
            'project_id',
            'submission_id'
            ],
        'submission':[
            'submitter',
            'comments'
            ],
        'illumina_adapter':[
            'number'
            ],
        'reagent':[
            'status',
            'price_per_unit',
            'reagent_active'
            ],
        'purchase_order':[
            'total_amount',
            'remaining_amount',
            'po_active',
            'pi'
            ],
        'sequencing_price':[
            'harvard_code_price',
            'paired_end',
            'read_length',
            'po_price',
            'commercial_price',
            'outside_academic_price'
            ],
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
base_date_col_map = ['last_modified', 'date_created', 'entry_date',
'valid_from_date', 'invoice_month', 'run_date']
# by table
date_col_map = {
    'oligo_order': [
        'request_date','order_date','cancel_date','receive_date'
    ],
    'invoice':[
        'month'
        ],
    'line_item':[
        'month',
        'delivery_date'
        ],
    'sample_sheet':[
        'date'
        ],
    'illumina_run':[
        'run_date'
        ],
    'illumina_bclconversion_analysis':['launch_timestamp'],
    'reagent_request':[
        'invoice_month'
        ]
}
fk_name_translate = {
        'submitter_name':'submitter',
        'expense_code_1':'expense_code',
        'sample_name':'sample_id',
        'investigatorname':'investigator',
        'investigator_name':'investigator',
        'lab_admin_name':'lab_admin'
        }
# fk field to table
fk_tbl_map = {
        'group_member': 'user',
        'group': 'organization',
        'operator':'user',
        'sample_name':'sample',
        'status': 'status',
        'plasmid': 'plasmid',
        'strain':'strain',
        'oligo':'oligo',
        'requester':'user',
        'orderer':'user',
        'receiver':'user',
        'canceler':'user',
        'pi':'user',
        'owner_institution':'institution',
        'submitter_name':'user',
        'investigatorname':'user',
        'investigator_name':'user',
        'experiment_name':'submission',
        'experimentname':'submission',
        'lab_admin_name':'user'
}

# use to just skip some troublesome rows
keys_to_skip = ['Weinstein_Bryan', 'Bryan Weinstein', 'Bryan_Weinstein',
        'Testy_McTesterson', 'Lester_Kobzik',
        'David_Doupe2','Kathy_LoBuglio','2150030660','0007281637']
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
        data.append(["", "", tbl, col, val])
    row_dict = {}
    for row in data:
        col = row[Column.property].lower()
        col = col.replace(" ",'_')
        col = re.sub('\s+','', col)
        val = row[Column.value]
        if val: # don't bother inserting nones
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
                    if func_name == 'user_org':
                        new_dict =  globals()[func_name](col, val, data)
                    else:
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
    if tbl == 'user' and 'email' in row_dict:
        id_exists = pk_exists(row_dict['email'], 'email', tbl)
        if id_exists:
            print("\t\tSkipping because " + row_dict['email'] + " already exists: " +
                    str(id_exists))
            return False
    elif tbl =='institution':
        id_exists = pk_exists(row_dict['name'], 'name', tbl)
        if id_exists:
            print("\t\tSkipping because " + row_dict['name'] + " already exists: " +
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
        insert = iggy_db.cursor()
        insert.execute(sql)
        iggy_db.commit()
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
    for row_num, row in enumerate(pks_rows):
        pk = row[0][0:50]
        if pk in keys_to_skip:
            continue
        print("\t" + str(row_num) + " Working on name: " + pk)
        tbl_name = thing
        print("\t\tMapping data for: " + tbl_name + ' into: ' + new_tbl)
        id_exists = pk_exists(pk, 'name', new_tbl, )
        if id_exists:
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
        new_col = fk_tbl_map[col]
    else:
        new_col = col

    if col == 'billable_item':
        if 'SUB' in val:
            new_col = 'submission'
        elif 'REA' in val:
            new_col = 'reagent_request'
        else:
            new_col = 'reagent_request'
    if new_col == 'user':
        val = val.replace(' ','_')
    fk_id = pk_exists(val, 'name', new_col)
    if not fk_id and new_col == 'user':
        fk_id = pk_exists(val, 'email', new_col)
    if fk_id:
        if new_col in ['status']:
            new_dict = {new_col: fk_id}
        elif col in ['canceler','receiver','requester','orderer', 'pi',
        'owner_institution', 'operator']:
            new_dict = {col: fk_id}
        elif col in ['billable_item']:
            if 'SUB' in val:
                new_dict = {'submission_id': fk_id}
            elif 'REA' in val:
                new_dict = {'reagent_request_id': fk_id}
            else:
                new_dict = {}
        elif col in fk_name_translate:
            new_dict = {fk_name_translate[col]: fk_id}
        else:
            new_dict = {(new_col + '_id'): fk_id}

    return new_dict

def make_numeric(col, val):
    new_dict = {}
    arr = re.split('[^0-9]', val)
    number = arr[0]
    if number == '':
        number = 'NULL'
    if col == 'volume_(ul)':
        new_dict = {'volume':number}
    else:
        new_dict = {col:number}
    return new_dict

def get_active(col, val):
    new_dict = {}
    if val == 'ACTIVE':
        new_dict = {'po_active':1}
    else:
        new_dict = {'po_active':0}
    return new_dict

def as_name(col, val):
    new_dict = {'name':val}
    return new_dict

def get_bool(col, val):
    new_dict = {}
    val.strip()
    if val == 'yes' or val == 'Y' or val == 'y':
        new_dict = {col:1}
    else:
        new_dict = {col:0}
    return new_dict


def get_status(col, val):
    new_dict = {}
    if fk_tbl_map[col]:
        new_tbl = fk_tbl_map[col]
        fk_id = pk_exists(val, 'name', new_tbl)
        if fk_id:
            new_dict = {(new_tbl + '_id'): fk_id}
    return new_dict

def insert_long_text(col, val):
    global iggy_db
    global max_id
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
    if not max_id:
        print('not max id')
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
    try:
        print("\t\t\t" + sql)
    except:
        print("\t\t\t" + 'sql has bad chars')
    note = iggy_db.cursor()
    note.execute(sql)
    iggy_db.commit()
    fk_id = note.lastrowid
    new_dict = {col_name: fk_id}
    return new_dict

def user_org(col, val, data):
    for row in data:
        if row[Column.property] == 'Name':
            val = row[Column.value]
    org_id = pk_exists(val, 'name', 'organization')
    if not org_id:
        org_id = do_insert('organization', {'name': val, 'active': 1,
            'organization_id':1})
    return {'organization_id': org_id}

mini_db = get_connection(
    config.RC_Development.PROJECT,
    config.RC_Development.DB_KEY,
    config.RC_Development.DB_ADDRESS,
    #'murraylabweb_minilims'
    'bauer_minilims'
)
iggy_db = get_connection(
    config.MYSQL_MPM_USER,
    config.MYSQL_MPM_PASS,
    'localhost',
    'iggybase'
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

# migrate_semantic_data()
# migrate_table('semantic_data', 'Group', 'organization')
# migrate_table('semantic_data', 'Group_Member', 'user')
# migrate_table('semantic_data', 'Project', 'project')
# migrate_table('semantic_data', 'Machine', 'machine')
# migrate_table('semantic_data', 'Invoice_Template', 'invoice_template')
# migrate_table('semantic_data', 'Reagent', 'reagent')
# migrate_table('semantic_data', 'Sequencing_Price', 'sequencing_price')
# migrate_table('semantic_data', 'Sequencing_Price', 'sequencing_price')
# migrate_table('bauer_semantic_data', 'Illumina_Adapter', 'illumina_adapter')
#migrate_table('bauer_semantic_data', 'Purchase_Order', 'purchase_order')
#migrate_table('bauer_semantic_data', 'Reagent_Request', 'reagent_request')
#migrate_table('bauer_semantic_data', 'Submission', 'submission')
#migrate_table('bauer_semantic_data', 'Sample', 'sample')
migrate_table('bauer_semantic_data', 'Sample_Sheet_Item', 'sample_sheet_item')
#migrate_table('bauer_semantic_data', 'Illumina_BclConversion_Analysis',
#'illumina_bclconversion_analysis')
#migrate_table('bauer_semantic_data', 'Illumina_Run', 'illumina_run')
#migrate_table('bauer_semantic_data', 'Sample_Sheet', 'sample_sheet')
#migrate_table('bauer_semantic_data', 'Illumina_Flowcell', 'illumina_flowcell')
#migrate_table('bauer_semantic_data', 'Line_Item', 'line_item')
#migrate_table('bauer_semantic_data', 'Invoice', 'invoice')

# Murray tables
# migrate_table('semantic_data', 'Strain', 'strain')
# migrate_table('semantic_data', 'Plasmid', 'plasmid')
# migrate_table('semantic_data', 'Fragment', 'fragment')
# migrate_table('semantic_data', 'Genotype', 'genotype')
# migrate_table('semantic_data', 'Oligo_Fragment', 'oligo_fragment')
# migrate_table('semantic_data', 'Oligo_Batch', 'oligo_order')

