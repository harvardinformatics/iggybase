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
        self.max_id = None
        self.from_db = self.get_connection(
            config.from_db['user'],
            config.from_db['password'],
            config.from_db['host'],
            config.from_db['database']
        )

    def make_dict(self, data, tbl):
        tbl = tbl.lower()
        col_name_map = self.get_map(tbl, 'col_name')
        col_value_map = self.get_map(tbl, 'col_value')
        add_cols = self.get_map(tbl, 'add_cols')

        for col, val in add_cols.items():
            data.append(["", "", tbl, col, val])
        row_dict = {}
        # get any function params from the row
        func_with_params = {}
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
                new_dict = {}
                # execute any funcs
                if col in col_value_map:
                    value_map = col_value_map[col]
                    if value_map:
                        if (isinstance(value_map, str) and 'func_' in value_map):
                            print(value_map)
                            func_name = value_map.replace('func_', '')
                            if func_name in config.func_params:
                                func_with_params[func_name] = {'new_col': new_col,
                                        'params': config.func_params[func_name],
                                        'val': val}
                            else:
                                if hasattr(self, func_name):
                                    new_dict =  getattr(self, func_name)(new_col, val, col_name_map)
                                else:
                                    print('Error, no function defined: ' + func_name)
                                    sys.exit(1)
                        else:
                            new_dict = {new_col: value_map}
                else:
                    new_dict = {new_col: val}
                if new_dict:
                    row_dict.update(new_dict)
        # call any functions that requrired other row values as params
        for func_name, func_info in func_with_params.items():
            func_params = [func_info['new_col'], func_info['val'], col_name_map]
            skip = False
            for param in func_info['params']:
                if param in row_dict:
                    func_params.append(row_dict[param])
                else:
                    skip = True
            if not skip:
                if hasattr(self, func_name):
                    new_dict = getattr(self, func_name)(*func_params)
                    if new_dict:
                        row_dict.update(new_dict)
                else:
                    print('Error, no function defined: ' + func_name)
                    sys.exit(1)
        if tbl in config.keys_to_delete:
            for key in config.keys_to_delete[tbl]:
                if key in row_dict:
                    del row_dict[key]
        print("\t\t" + str(row_dict))
        return row_dict


    def semantic_select_row(self, pk, thing, property, tbl):
        where = "name ='" + pk.replace("'","\\\'") + "'"
        sql = ('Select * from ' + tbl + " where thing = '" + thing
            + "' and property = '" + property + "' and " + where + ' limit 1')
        print(sql)
        exist = self.from_db.cursor()
        exist.execute(sql)
        row = exist.fetchone()
        return row

    def get_col_name(self, col, col_name_map):
        if col in col_name_map:
            return col_name_map[col]
        return col

    def split_name(self, col, val, col_name_map):
        if '_' in val:
            names = val.split('_', 1)
            first, last = names[0], names[1]
        else:
            first = val
            last = ''
        new_dict = {'first_name': first, 'last_name': last}
        return new_dict

    def get_fk(self, col, val, col_name_map):
        new_dict = {}
        if col in config.fk_tbl_map:
            new_col = config.fk_tbl_map[col]
        else:
            new_col = col
        if col == 'invoice_organization':
            fk_id = self.pk_exists(val, 'name', 'organization')
        else:
            fk_id = self.pk_exists(val, 'name', new_col)
        if fk_id:
            if col in col_name_map:
                new_dict = {col_name_map[col]: fk_id}
            else:
                new_dict = {(new_col + '_id'): fk_id}
        return new_dict

    def price_per_unit(self, col, val, col_name_map, quantity):
        new_dict = self.make_numeric(col, val, col_name_map)
        if int(quantity) < 1:
            quantity = 1
        new_dict[self.get_col_name(col, col_name_map)] = (int(new_dict[self.get_col_name(col, col_name_map)])/int(quantity))
        return new_dict

    def make_numeric(self, col, val, col_name_map):
        new_dict = {}
        val = val.replace(',', '')
        arr = re.split('[^0-9]', val)
        number = arr[0]
        if number == '':
            number = 'NULL'
        else:
            new_dict = {self.get_col_name(col, col_name_map):number}
        return new_dict

    def get_active(self, col, val, col_name_map):
        new_dict = {}
        col_name = self.get_col_name(col, col_name_map)
        if val == 'ACTIVE':
            new_dict = {col_name:1}
        else:
            new_dict = {col_name:0}
        return new_dict

    def get_bool(self, col, val, col_name_map):
        new_dict = {}
        val.strip()
        col_name = self.get_col_name(col, col_name_map)
        if val == 'yes' or val == 'Y' or val == 'y':
            new_dict = {col_name:1}
        else:
            new_dict = {col_name:0}
        return new_dict

    def get_status(self, col, val, col_name_map):
        new_dict = {}
        if fk_tbl_map[col]:
            new_tbl = fk_tbl_map[col]
            fk_id = self.pk_exists(val, 'name', new_tbl)
            if fk_id:
                new_dict = {(new_tbl + '_id'): fk_id}
        return new_dict

    def insert_long_text(self, col, val, col_name_map):
        if col in col_name_map:
            col_name = col_name_map[col]
        else:
            col_name = col
        # check if the long_text exists
        sql = 'select id from long_text where long_text = "' + val.replace('"','') + '"'
        long_text = self.to_db.cursor()
        long_text.execute(sql)
        long_text = long_text.fetchone()
        if long_text and long_text[0]:
            return {col_name: long_text[0]}
        if not self.max_id:
            sql = 'select max(id) from long_text'
            get_max_id = self.to_db.cursor()
            get_max_id.execute(sql)
            self.max_id = get_max_id.fetchone()
            if self.max_id:
                self.max_id = self.max_id[0]
        if not self.max_id:
            self.max_id = 1
        else:
            self.max_id = self.max_id + 1
        # TODO: we need to fix name to not have constant 4 zeros
        if len(str(self.max_id)) == 1:
            name = 'LT00000' + str(self.max_id)
        else:
            name = 'LT0000' + str(self.max_id)
        sql = (
            'insert into long_text (name, active, organization_id, long_text)'
            + ' values("' + name + '", 1, 8, "' + val.replace('"','') + '")'
        )
        try:
            print("\t\t\t" + sql)
        except:
            print("\t\t\t" + 'sql has bad chars')
        note = self.to_db.cursor()
        note.execute(sql)
        self.to_db.commit()
        fk_id = note.lastrowid
        new_dict = {col_name: fk_id}
        return new_dict

    def get_fk_billable(self, col, val, col_name_map, organization_id,  billable_item_type):
        new_dict = {}
        new_col = 'order'
        fk_id = self.pk_exists(val, 'name', new_col)
        if fk_id:
            new_dict = {'order_id': fk_id}
        if billable_item_type == 'Reagent_Request':
            print('reagent')
            row = self.semantic_select_row(val, 'Reagent_Request', 'Reagent',
            self.cli['semantic_source'])
            price_item_name = row[config.semantic_col_map['value']]
            print(price_item_name)
            id_exists = self.pk_exists(price_item_name, 'name', 'price_item')
            print(id_exists)
            if id_exists:
                new_dict[self.get_col_name(col, col_name_map)] = id_exists
        return new_dict

    def get_org_fk_user(self, col, val, col_name_map):
        user_data = self.get_fk_user(col, val, col_name_map)
        if 'user_id' in user_data:
            user_id = user_data['user_id']
            org_row = self.select_row('user_organization', {'user_id': user_id}, 1)
            if org_row:
                org_id = org_row[9]
                return {'organization_id': org_id, 'submitter_id': user_id}
        return None


    def get_fk_user(self, col, val, col_name_map):
        if col in col_name_map:
            col = col_name_map[col]
        if col == 'user':
            val = val.replace(' ','_')
        fk_id = self.pk_exists(val, 'name', col)
        if not fk_id and col == 'user':
            fk_id = self.pk_exists(val, 'email', col)
        new_dict = {}
        if fk_id:
            if col in ['canceler','receiver','requester','orderer', 'pi',
            'owner_institution', 'operator']:
                new_dict = {col: fk_id}
            elif col in col_name_map:
                new_dict = {col_name_map[col]: fk_id}
            else:
                new_dict = {(col + '_id'): fk_id}
        return new_dict

    def insert_charge_method(self, col, val, col_name_map, charge_type):
        print('charge')
        charge_method_id = self.pk_exists(val, 'code', 'charge_method')
        print(charge_method_id)
        if not charge_method_id:
            if charge_type == 'Purchase_Order':
                charge_method_type_id = 1
            else:
                charge_method_type_id = 2
                name, next_num = self.get_next_name('charge_method')
                row_dict = {
                        'name': name,
                        'charge_method_type_id': charge_method_type_id,
                        'organization_id': 1,
                        'code': val,
                        'active': 1,
                }
                row = self.do_insert('charge_method', row_dict)
                print(row)
                if row:
                    to = self.select_row('table_object',
                    {'name':'charge_method'})
                    to_id = to[0]
                    updated = self.update_row('table_object', {'id':
                        to_id}, {'new_name_id': next_num})
        return None


    def limit_val(self, col, val, col_name_map):
        val = val[0:50]
        new_dict = {self.get_col_name(col, col_name_map): val}
        return new_dict

    def get_reagent_price_item(self, col, val, col_name_map, organization_id,
            billable_item):
        new_dict = {}
        print(val)
        print(col)
        sys.exit(1)
        if val == 'Reagent_Request':
            print('reagent')
            row = self.semantic_select_row(billable_item, 'Reagent_Request', 'Reagent',
            self.cli['semantic_source'])
            price_item_name = row[config.semantic_col_map['value']]
            print(price_item_name)
            id_exists = self.pk_exists(price_item_name, 'name', 'price_item')
            print(id_exists)
            new_dict = {self.get_col_name(col, col_name_map): id_exists}
        return new_dict

    def get_price_item(self, col, val, col_name_map, organization_id):
        new_dict = {}
        row = self.semantic_select_row(val, 'Sequencing_Price', 'Display_Name',
        self.cli['semantic_source'])
        price_item_name = row[config.semantic_col_map['value']]
        id_exists = self.pk_exists(price_item_name, 'name', 'price_item')
        if id_exists:
            new_dict = {self.get_col_name(col, col_name_map): id_exists}
        return new_dict

    def find_user(self, pk):
        row = self.semantic_select_row(pk, 'Group_Member', 'Email',
        self.cli['semantic_source'])
        email = None
        if row:
            email = row[3]
        sql = 'select id from user where name = "' + pk.replace('"','') + '"'
        if email:
            sql += ' or email = "' + email + '"'
        sql += ' limit 1'
        pk_user = self.to_db.cursor()
        pk_user.execute(sql)
        user_id = pk_user.fetchone()
        print(user_id)
        if user_id:
            return user_id[0]
        else:
            return None


    def migrate_table(self, mini_table, thing, new_tbl):
        print("Table: " + mini_table + " thing: " + thing)
        pks = self.from_db.cursor()
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
            if new_tbl == 'user':
                id_exists = self.find_user(pk)
            else:
                id_exists = self.pk_exists(pk, 'name', new_tbl, )
            if id_exists and not no_skip:
                print("\t\tSkipping because " + pk + " already exists: " +
                        str(id_exists))
            else:
                data  = self.from_db.cursor()
                sql = (
                    "select * from " + mini_table
                    + " where name='" + pk
                    + "' and thing='" + tbl_name + "'"
                )
                print(sql)
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
        self.migrate_table(self.cli['semantic_source'], self.cli['from_tbl'], self.cli['to_tbl'])

# execute run on this class
script = MigrateScript()
script.run()
