import sys
import os

# add iggybase root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import datetime
import json
from dateutil.relativedelta import relativedelta
import glob
from xml.etree import ElementTree
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

def do_insert(tbl, row_dict):
    global iggy_db

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

def make_dict_illumina_run(run, pk):
    machine = pk_exists(run.findall('Instrument')[0].text, 'name', 'machine')
    run_dict = {
        'name': pk,
        'number': run.attrib.get('Number'),
        'machine_id': machine

    }
    for read in run.findall('Reads')[0].findall('Read'):
        num = read.attrib.get('Number')
        prefix = 'read_' + num
        run_dict[prefix + '_cycles'] = read.attrib.get('NumCycles')
        if read.attrib.get('IsIndexedRead') == 'Y':
            index = 1
        else:
            index = 0
        run_dict[prefix + '_index'] =  index
    return run_dict

def make_dict_illumina_flowcell(run, pk):
    row_dict = {}
    '''machine = pk_exists(run.findall('Instrument')[0].text, 'name', 'machine')
    run_dict = {
        'name': pk,
        'number': run.attrib.get('Number'),
        'machine_id': machine

    }
    for read in run.findall('Reads')[0].findall('Read'):
        num = read.attrib.get('Number')
        prefix = 'read_' + num
        run_dict[prefix + '_cycles'] = read.attrib.get('NumCycles')
        if read.attrib.get('IsIndexedRead') == 'Y':
            index = 1
        else:
            index = 0
        run_dict[prefix + '_index'] =  index'''
    return row_dict

def insert_row(table, pk):
    exists = pk_exists(pk, 'name', table)
    if not exists:
        print("\t\tgetting data for " + table + ": " + pk)
        func_name = 'make_dict_' + table
        if not func_name in globals():
            print("\t\tno func " + func_name + " defined")
            success = False
        else:
            dict_func = globals()['make_dict_' + table]
            row_dict = dict_func(run, pk)
            if row_dict:
                print("\t\trow data:" + json.dumps(row_dict))
                print("\t\t" + table + ": " + pk)
                success = do_insert(table, row_dict)
            else:
                print("\t\trow data empty")
                success = False
    else:
        print("\t\t" + table + ": " + pk + 'already exists, id: ' + str(exists))

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
for file in files:
    print("\tstarting to process file: " + file)
    # TODO: not all will be xml, consider an object eventually
    run_info = ElementTree.parse(file).getroot()
    print("\tprocessing " + str(len(run_info)) + ' runs')
    for run in run_info:
        insert_row('illumina_run', run.attrib.get('Id'))
        insert_row('illumina_flowcell', run.attrib.get('Id'))
