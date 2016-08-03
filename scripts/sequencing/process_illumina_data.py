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
    sql = 'Select ' + select + ' from ' + tbl + " where " + where
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

def parse_sample_sheet(data, pk):
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
        'illumina_run_id': run_id
    }
    return row_dict

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
    row_id = row_exists(ss_table, ss_name)
    if not row_id:
        row_dict = parse_sample_sheet(ss_name, row_id)
        row_dict.update({'file': file})
        if row_dict:
            do_insert(ss_table, row_dict)

    contents = open(file, 'rt')
    try:
        ss_dict = {}
        ss = csv.reader(contents)
        for row in ss:
            if row and '[' in row[0]:
                header = row[0].replace('[', '').replace(']', '').lower()
            elif header and row:
                if header in ss_dict:
                    ss_dict[header].append(row)
                else:
                    ss_dict[header] = [row]
    finally:
        contents.close()
    #print("\tprocessing " + str(len(run_info)) + ' runs')

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
    path = '/Users/portermahoney/sites/analysis_finished'

if 'filename' not in cli:
    print('You must have the option filename, exp:'
        + ' python process_seq_file.py --path=~sites/analysis_finished'
        + ' --filename=RunInfo.xml')
    sys.exit(1)

# get a db connection
iggy_db = get_connection(
        config.db['user'],
        config.db['password'],
        config.db['host'],
        config.db['database'])

# check path for filename
print('Checking for filename: ' + cli['filename'] + ' in dir: ' + path)
today = datetime.datetime.now()
yesterday = today + relativedelta(days=-1)
# within two days, TODO: days could be a cli
days = [today.strftime("%y%m%d"), yesterday.strftime("%y%m%d")]
days = ['160720', '160721'] # TODO: remove, this is for testing
files = []
for day in days:
    file_path = path + '/' + day + '*/' + cli['filename']
    files.extend(glob.glob(file_path))

print("\tfound " + str(len(files)) + " files to process")
file_func = globals()['process_file_' + (cli['filename'].split('.')[0].lower())]
for file in files:
    print("\tstarting to process file: " + file)
    file_func(file)
