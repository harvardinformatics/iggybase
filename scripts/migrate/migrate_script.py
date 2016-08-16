#import mysql.connector
#from datetime import datetime

import sys
import os

# add iggybase root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import datetime
import re
import time
import json
from dateutil.relativedelta import relativedelta
import glob
from xml.etree import ElementTree
import csv
from scripts.iggy_script import IggyScript
import migrate_config as config
from migrate_functions import *

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

class MigrateScript (IggyScript):
    def __init__(self):
        super(MigrateScript, self).__init__(config)
        self.to_db = self.db

        self.from_db = self.get_connection(
            config.from_db['user'],
            config.from_db['password'],
            config.from_db['host'],
            config.from_db['database']
        )

    '''def make_dict(data, tbl):
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
        return row_id'''

    def migrate_table(mini_table, thing, new_tbl):
        print("Table: " + mini_table + " thing: " + thing)
        pks = self.to_db.cursor()
        sql = "select distinct name from " + mini_table + " where thing = '" + thing + "'"
        if 'limit' in self.cli:
            sql += ' limit ' + self.cli['limit']
        pks.execute(sql)
        pks_rows = pks.fetchall()
        if 'start' in self.cli:
            pks_rows = pks_rows[int(self.cli['start']):]
        print('found rows: ' + str(len(pks_rows)))
        no_skip = False
        if 'no_skip' in self.cli:
            if self.cli['no_skip'] == '1':
                no_skip = True
        for row_num, row in enumerate(pks_rows):
            pk = row[0]
            if pk in self.get_config('keys_to_skip'):
                continue
            print("\t" + str(row_num) + " Working on name: " + pk)
            tbl_name = thing
            print("\t\tMapping data for: " + tbl_name + ' into: ' + new_tbl)
            id_exists = self.pk_exists(pk, 'name', new_tbl, )
            if id_exists and not no_skip:
                print("\t\tSkipping because " + pk + " already exists: " +
                        str(id_exists))
            else:
                data  = self.to_db.cursor()
                sql = (
                    "select * from " + mini_table
                    + " where name='" + pk
                    + "' and thing='" + tbl_name + "'"
                )
                data.execute(sql)
                data = data.fetchall()
                row_dict = self.make_dict(data, tbl_name)
                row = self.do_insert(new_tbl, row_dict)
            print('\tCompleted work on name: ' + pk + "\n\n")
        print('Completed table: ' + mini_table + " thing: " + thing + "\n\n\n\n")



    def parse_cli(self):
        cli = super(MigrateScript, self).parse_cli()
        if 'semantic_source' in cli and 'from_tbl' in cli and 'to_tbl' in cli:
            print(("Semantic Source: " + cli['semantic_source'] + " from_tbl: " +
                    cli['from_tbl'] + ' to_tbl: ' + cli['to_tbl']))
        else:
            print("Please enter the following required parameters\n\n")
            if 'semantic_source' not in cli:
                cli['semantic_source'] = input("Enter the semantic source table:\n")
            if 'from_tbl' not in cli:
                cli['from_tbl'] = input("Enter the value representing the semantic group for this table:\n")
            if 'to_tbl' not in cli:
                cli['to_tbl'] = input("Enter the name table to migrate to:\n")
        return cli

    def run(self):
        migrate_table(self.cli['semantic_source'], self.cli['from_tbl'], self.cli['to_tbl'])

# execute run on this class
script = MigrateScript()
script.run()
