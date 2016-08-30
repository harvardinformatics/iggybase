import sys
import os

# add iggybase root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import time
import datetime
import json
import mysql.connector
import scripts.iggy_script_config as base_config

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

class IggyScript:

    def __init__(self, config = None):
        self.cli = self.parse_cli()
        self.config = config
        # get a db connection
        db_config = self.get_config('db')
        self.db = self.get_connection(db_config['user'],
                db_config['password'],
                db_config['host'],
                db_config['database'])

    def get_connection(self, user, password, host, database):
            db = mysql.connector.connect(
                user = user,
                password = password,
                host = host,
                database = database)
            return db

    # if child passes in a config it will override the base
    def get_config(self, param):
        val = getattr(self.config, param, None)
        if not val:
            val = getattr(base_config, param)
        return val

    def pk_exists(self, pk, name, tbl, select = 'id'):
        if isinstance(pk, str):
            where = name + "='" + pk.replace("'","\\\'") + "'"
        else:
            where = name + "=" + str(pk)
        sql = 'Select ' + select + ' from `' + tbl + "` where " + where
        exist = self.db.cursor()
        exist.execute(sql)
        row = exist.fetchone()
        if row:
            row_id = row[0]
        else:
            row_id = None
        return row_id

    def get_map(self, tbl, prefix, is_list = False):
        map_name = prefix + '_map'
        base_map_name = 'base_' + map_name
        base_map = self.get_config(base_map_name)
        map_by_table = self.get_config(map_name)
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

    def make_vals(self, tbl, cols):
        val_str = ""
        int_cols = self.get_map(tbl, 'int_col', True)
        date_cols = self.get_map(tbl, 'date_col', True)
        i = 0
        for col, val in cols.items():
            if val is not None:
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

    def add_cols(self, tbl, row_dict):
        base_cols = self.get_map(tbl, 'add_cols')
        row_dict.update(base_cols)
        return row_dict

    def do_insert(self, tbl, row_dict):
        row_dict = self.add_cols(tbl, row_dict)
        print("\t\tinserting into " + tbl + " row data:" + json.dumps(row_dict))
        val_str = self.make_vals(tbl, row_dict)
        sql = 'Insert into `' + tbl + '` (`' + '`,`'.join(list(row_dict.keys())) + '`) values(' + val_str + ')'
        try:
            print("\t\t" + sql)
        except:
            print("\t\t" + 'sql has bad characters')
        if 'insert_mode' in self.cli:
            insert_mode = True
        else:
            insert_mode = False
            print("\t\tNo insert: use opt --insert_mode to actually insert")

        ret = False
        if insert_mode:
            insert = self.db.cursor()
            insert.execute(sql)
            self.db.commit()

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

    # TODO: compare with pk_exists and row_exists
    def select_row(self, tbl, criteria = [], limit = 1):
        int_cols = self.get_map(tbl, 'int_col', True)
        pks = self.db.cursor()
        sql = "select * from " + tbl
        wheres = []
        for key, val in criteria.items():
            if key in int_cols:
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

    def update_row(self, tbl, criteria, cols):
        if 'insert_mode' in self.cli:
            pks = self.db.cursor()
            sql = "update `" + tbl + '`'
            int_cols = self.get_map(tbl, 'int_col', True)
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
            self.db.commit()

    def update_table_status(self, table, ids, status, current = []):
        table_object_id = self.pk_exists(table, 'name', 'table_object')
        status_row = self.select_row('status', {'name': status, 'table_object_id':
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
                status_row = self.select_row('status', {'name': c, 'table_object_id':
                    table_object_id})
                if status_row:
                    curr_status.append(status_row[0])
            if curr_status:
                criteria['status_id'] = curr_status
            self.update_row(
                    table,
                    criteria,
                    cols
            )

    def get_next_name(self, table_name):
        table_meta = self.select_row('table_object', {'name':
            table_name})
        name = table_meta[9]
        num = table_meta[10]
        next_num = num + 1
        dig = table_meta[11] - len(str(num))
        for i in range(0,dig):
            name += '0'
        name += str(num)
        return name, next_num

    def row_exists(self, table, pk):
        exists = self.pk_exists(pk, 'name', table)
        if exists:
            print("\t\t" + table + ": " + pk + 'already exists, id: ' + str(exists))
        return exists

    def parse_cli(self):
        cli = {}
        args = sys.argv[1:]
        for arg in args:
            pair = arg.split('=',1)
            name = pair[0]
            val = True
            if len(pair) > 1:
                val = pair[1]
            cli[name.replace('--','')] = val
        print(cli)
        return cli

    def run(self):
        raise NotImplementedError()
