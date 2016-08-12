import sys
import os

# add iggybase root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import datetime
import time
import json
from dateutil.relativedelta import relativedelta
import glob
from xml.etree import ElementTree
import csv
import mysql.connector
import illumina_data_config as config

"""
script for inserting illumina_run data

CLI options include
    --insert_mode: will actually do the inserts
    --path: path to the file containing directories of illumina data
    --filename: what file to process, exp RunInfo.xml

exp use:
python process_illumina_data.py --insert_mode --path='/n/seq/sequencing/'
    --filename=RunInfo.xml
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

def pk_exists(pk, name, tbl, select = 'id'):
    global iggy_db
    if isinstance(pk, str):
        where = name + "='" + pk.replace("'","\\\'") + "'"
    else:
        where = name + "=" + str(pk)
    sql = 'Select ' + select + ' from `' + tbl + "` where " + where
    exist = iggy_db.cursor()
    exist.execute(sql)
    row = exist.fetchone()
    if row:
        row_id = row[0]
    else:
        row_id = None
    return row_id

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
            if val == 'now':
                val = str(int(time.time()))
            if '-' in val:
                date_formats = [ '%Y-%m-%d', '%Y-%m', '%Y-%m-%d %H:%M:%S']
                for date_format in date_formats:
                    try:
                        val_str += '"' + str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(val,
                    date_format)))) + '"'
                        formatted = True
                        break
                    except:
                        pass
            elif ':' in val:
                try:
                    date_format = '%b %d %Y %H:%M:%S'
                    val_str += '"' + str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(val,
                date_format)))) + '"'
                    formatted = True
                except:
                    val_str += 'Null'

            elif '/' in val:
                date_formats = ['%m/%d/%y',  '%-m/%d/%y']
                for date_format in date_formats:
                    try:
                        val_str += '"' + str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(val,
                        date_format)))) + '"'
                        formatted = True
                        break
                    except:
                        pass
            else:
                val_str += '"' + str(datetime.datetime.fromtimestamp(int(val))) + '"'
                formatted = True
            if not formatted:
                val_str += 'Null'
                print('Date could not be formated ' + str(val))
        else:
            val.replace("'","\'")
            val_str += '"' + val.replace('"','') + '"'
        i += 1
    return val_str

def do_insert(tbl, row_dict):
    global iggy_db

    print("\t\tinserting into " + tbl + " row data:" + json.dumps(row_dict))
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

def update_row(tbl, criteria, cols):
    global cli
    if 'insert_mode' in cli:
        pks = iggy_db.cursor()
        sql = "update `" + tbl + '`'
        int_cols = get_map(tbl, 'int_col', True)
        for name, val in cols.items():
            if name in int_cols:
                sql += ' set ' + name + ' = ' + str(val)
            else:
                sql += ' set ' + name + ' = "' + val + '"'
        sql += ' where '
        wheres = []
        for key, crit in criteria.items():
            if isinstance(crit, list) and crit:
                if key in int_cols:
                    wheres.append(key + ' in (' + ','.join([str(c) for c in crit]) + ')')
                else:
                    wheres.append(key + ' in ("' + '","'.join(crit) + '")')
            else:
                if key in int_cols:
                    wheres.append(key + ' = ' + str(crit))
                else:
                    wheres.append(key + ' = "' + str(crit) + '"')
        sql += ' and '.join(wheres)
        print("\t\t" + sql)
        pks.execute(sql)
        iggy_db.commit()

def update_table_status(table, ids, status, current = []):
    table_object_id = pk_exists(table, 'name', 'table_object')
    status_row = select_row('status', {'name': status, 'table_object_id':
        table_object_id})
    if status_row:
        cols = {
                'status_id': status_row[0],
        }
        criteria = {
                'id': ids
        }
        curr_status = []
        for c in current:
            status_row = select_row('status', {'name': c, 'table_object_id':
                table_object_id})
            if status_row:
                curr_status.append(status_row[0])
        if curr_status:
            criteria['status_id'] = curr_status
        update_row(
                table,
                criteria,
                cols
        )

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

def parse_illumina_run(data, pk):
    machine = pk_exists(data.findall('Instrument')[0].text, 'name', 'machine')
    row_dict = {
        'name': pk,
        'number': data.attrib.get('Number'),
        'machine_id': machine,
        'status': 'new'
    }
    for read in data.findall('Reads')[0].findall('Read'):
        num = read.attrib.get('Number')
        prefix = 'read_' + num
        row_dict[prefix + '_cycles'] = read.attrib.get('NumCycles')
        if read.attrib.get('IsIndexedRead') == 'Y':
            index = 1
        else:
            index = 0
        row_dict[prefix + '_index'] =  index
    return row_dict

def parse_illumina_flowcell(data, pk):
    flowcell_layout = data.findall('FlowcellLayout')[0]
    row_dict = {
        'name': pk,
        'lane_count': flowcell_layout.get('LaneCount'),
        'surface_count': flowcell_layout.get('SurfaceCount'),
        'swath_count': flowcell_layout.get('SwathCount'),
        'tile_count': flowcell_layout.get('TileCount'),
        'status': 'new'
    }
    return row_dict

def parse_sample_sheet(data, file):
    data_split = data.split('_')
    machine_id = pk_exists(data_split[1], 'name', 'machine')
    flowcell_id = pk_exists(data_split[3][1:], 'name', 'illumina_flowcell')
    run_id = pk_exists(flowcell_id, 'id', 'illumina_flowcell', 'illumina_run_id')
    row_dict = {
        'name': data,
        'run_date': (data_split[0][2:4] + '/' + data_split[0][4:6] + '/' + data_split[0][0:2]),
        'machine_id': machine_id,
        'slot': data_split[3][0:1],
        'illumina_flowcell_id': flowcell_id,
        'illumina_run_id': run_id,
        'file': file,
        'date_created': 'now'
    }
    return row_dict

def parse_sample_sheet_item(data):
    row_dict = {
        'index': data['index'],
        'order_id': data['order_id'],
        'sample_sheet_id': data['sample_sheet_id'],
        'date_created': 'now'
    }
    if 'lane' in data:
        row_dict['lane'] = data['lane']
    return row_dict

def get_sample_sheet_item_id(run_id, order_id, index, lane = None):
    global iggy_db
    sql = ('select i.id from sample_sheet_item i'
        ' inner join sample_sheet s on i.sample_sheet_id = s.id'
        ' where s.illumina_run_id = ' + str(run_id)
        + ' and i.order_id = ' + str(order_id)
        + ' and i.index = "' + index + '"')
    if lane:
        sql += ' and i.lane = ' + lane
    print("\t\t" + sql)
    exist = iggy_db.cursor()
    exist.execute(sql)
    row = exist.fetchone()
    row_id = None
    if row:
        row_id = row[0]
    return row_id

def insert_sample_sheet_items(rows):
    inserted = 0
    skipped = 0
    failed = 0
    si_table = 'sample_sheet_item'
    print("\t\tfound " + str(len(rows)) + ' sample sheet items to enter')
    for row in rows:
        if row['illumina_run_id'] and row['order_id'] and row['index']:
            row_id = get_sample_sheet_item_id(
                    row['illumina_run_id'],
                    row['order_id'],
                    row['index'],
                    row.get('lane', None)
            )
            if not row_id:
                row_dict = parse_sample_sheet_item(row)
                name, next_num = get_next_name(si_table)
                row_dict.update({'name': name})
                si_id = do_insert(si_table, row_dict)
                if si_id:
                    update_row(
                            'table_object',
                            {'name': si_table},
                            {'new_name_id': next_num}
                    )
                    inserted += 1
            else:
                skipped += 1
        else:
            print("\t\tnot enough infomation provided")
            failed += 1
        print("\n\n")
    print("\t\tinserted " + str(inserted)
            + " skipped " + str(skipped)
            + " failed " + str(failed)
            + " total = " + str(inserted + skipped + failed)
            + " sample sheet items out of " + str(len(rows)))

def parse_hiseq(lines, illumina_run_id, ss_id):
    item_cols = [i.lower() for i in lines[0]]
    rows = []
    order_ids = []
    for row in lines[1:]:
        row_dict = dict(zip(item_cols, row))
        if 'description' in row_dict:
            order_id = pk_exists(row_dict['description'], 'name', 'order')
            if order_id:
                order_ids.append(order_id)
        row_dict.update({
            'order_id': order_id,
            'sample_sheet_id': ss_id,
            'illumina_run_id': illumina_run_id
        })
        rows.append(row_dict)
    return order_ids, rows

def parse_miseq(file_dict, illumina_run_id, ss_id):
    order_ids = []
    if 'header' in file_dict and file_dict['header'][2][1]:
        order_id = pk_exists(file_dict['header'][2][1], 'name', 'order')
    rows = []
    if order_id:
        item_cols = [i.lower() for i in file_dict['data'][0]]
        for row in file_dict['data'][1:]:
            row_dict = dict(zip(item_cols, row))
            row_dict.update({
                'order_id': order_id,
                'illumina_run_id': illumina_run_id,
                'sample_sheet_id': ss_id
            })
            rows.append(row_dict)
        order_ids.append(order_id)
    return order_ids, rows

def row_exists(table, pk):
    exists = pk_exists(pk, 'name', table)
    if exists:
        print("\t\t" + table + ": " + pk + 'already exists, id: ' + str(exists))
    return exists

def process_file_runinfo(file):
    run_info = ElementTree.parse(file).getroot()
    print("\tprocessing " + str(len(run_info)) + ' runs')
    for run in run_info:
        run_table = 'illumina_run'
        run_name = run.attrib.get('Id')
        run_id = row_exists(run_table, run_name)
        if not run_id:
            row_dict = parse_illumina_run(run, run_name)
            if row_dict:
                run_id = do_insert(run_table, row_dict)
        if run_id:
            flow_table = 'illumina_flowcell'
            flow_name = run.findall('Flowcell')[0].text
            flow_id = row_exists(flow_table, flow_name)
            if not flow_id:
                row_dict = parse_illumina_flowcell(run, flow_name)
                if row_dict:
                    row_dict.update({'illumina_run_id': run_id})
                    do_insert(flow_table, row_dict)

def process_file_samplesheet(file):
    global path
    global cli
    ss_name = (file.replace(path, '')
        .replace(cli['filename'], '')
        .replace('/', ''))

    ss_table = 'sample_sheet'
    ss_id = row_exists(ss_table, ss_name)
    ss_dict = parse_sample_sheet(ss_name, file)
    if ss_dict:
        contents = open(file, 'rt')
        illumina_run_id = ss_dict['illumina_run_id']
        try:
            lines = list(csv.reader(contents))
            if lines[0][0] == '[Header]':
                file_dict = {}
                for row in lines:
                    if row and '[' in row[0]:
                        header = row[0].replace('[', '').replace(']', '').lower()
                    elif header and row:
                        if header in file_dict:
                            file_dict[header].append(row)
                        else:
                            file_dict[header] = [row]
                if ('settings' in file_dict):
                    count = len(file_dict['settings'])
                    if file_dict['settings'][0] and file_dict['settings'][0][0].lower() == 'adapter':
                        ss_dict['adapter_1'] = file_dict['settings'][0][1]
                    # TODO: consider max here or create new table
                    '''if count > 1:
                        adaptor_num = 2
                        for setting in file_dict['settings'][1:]:
                            if len(setting) > 1:
                                ss_dict['adapter_' + adaptor_num] = setting[1]
                            adaptor_num += 1 '''
                if ('reads' in file_dict
                        and file_dict['reads']
                        and file_dict['reads'][0]
                ):
                    ss_dict['read_length_1'] = file_dict['reads'][0][0]
                if not ss_id:
                    ss_id = do_insert(ss_table, ss_dict)
                order_ids, rows = parse_miseq(file_dict, illumina_run_id, ss_id)
            else:
                if not ss_id:
                    ss_id = do_insert(ss_table, ss_dict)
                order_ids, rows = parse_hiseq(lines, illumina_run_id, ss_id)
            if ss_id:
                insert_sample_sheet_items(rows)
            if order_ids:
                if folder == 'primary_data':
                    update_table_status('order', list(set(order_ids)), 'running', ['new'])
                else:
                    update_table_status('order', list(set(order_ids)), 'in analysis', ['new',
                    'running'])
        finally:
            contents.close()

args = sys.argv[1:]
for arg in args:
    pair = arg.split('=',1)
    name = pair[0]
    val = True
    if len(pair) > 1:
        val = pair[1]
    cli[name.replace('--','')] = val
print(cli)

if 'path' in cli:
    path = cli['path']
else:
    # TODO: replace with real default after testing
    path = '/Users/portermahoney/sites/primary_data'
folder = path.split('/')[-1]

if 'filename' in cli:
    filename = cli['filename']
else:
    print('You must have the option filename, exp:'
        + ' python process_seq_file.py --path=~sites/analysis_finished'
        + ' --filename=RunInfo.xml')
    sys.exit(1)

if 'dir_match' in cli:
    dir_match = cli['dir_match']
else:
    dir_match = ''

# get a db connection
iggy_db = get_connection(
        config.db['user'],
        config.db['password'],
        config.db['host'],
        config.db['database'])

# check path for filename
print('Checking for filename: ' + filename + ' in dir: ' + path)
today = datetime.datetime.now()
yesterday = today + relativedelta(days=-1)
# within two days, TODO: days could be a cli
days = [today.strftime("%y%m%d"), yesterday.strftime("%y%m%d")]
days = ['160720', '160721'] # TODO: remove, this is for testing
files = []
for day in days:
    file_path = path + '/' + day + '*' + dir_match + '*/' + filename
    files.extend(glob.glob(file_path))
print("\tfound " + str(len(files)) + " files to process")
process_func = globals()['process_file_' + (filename.split('.')[0].lower())]

for file in files:
    print("\tstarting to process: " + file)
    process_func(file)
    print("\n\n\n\n")
