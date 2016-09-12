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

class MigrateCustomScript (IggyScript):
    def __init__(self):
        super(MigrateCustomScript, self).__init__(config)
        self.to_db = self.db
        self.max_id = None
        self.from_db = self.get_connection(
            config.from_db['user'],
            config.from_db['password'],
            config.from_db['host'],
            config.from_db['database']
        )

    def make_dict(self, data, tbl):
        print(tbl)
        print(data)
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
                # execute any funcs
                if col in col_value_map:
                    value_map = col_value_map[col]
                    if value_map:
                        if 'func_' in value_map:
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
                row_dict.update(new_dict)
        # call any functions that requrired other row values as params
        for func_name, func_info in func_with_params.items():
            func_params = [func_info['new_col'], func_info['val'], col_name_map]
            for param in func_info['params']:
                func_params.append(row_dict[param])
            if hasattr(self, func_name):
                new_dict = getattr(self, func_name)(*func_params)
                row_dict.update(new_dict)
            else:
                print('Error, no function defined: ' + func_name)
                sys.exit(1)
        print("\t\t" + str(row_dict))
        return row_dict


    def semantic_select_row(self, pk, thing, property, tbl):
        where = "name ='" + pk.replace("'","\\\'") + "'"
        sql = ('Select * from ' + tbl + " where thing = '" + thing
            + "' and property = '" + property + "' and " + where)
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
        fk_id = self.pk_exists(val, 'name', new_col)
        if fk_id:
            if col in col_name_map:
                new_dict = {col_name_map[col]: fk_id}
            else:
                new_dict = {(new_col + '_id'): fk_id}
        return new_dict

    def price_per_unit(self, col, val, col_name_map, quantity):
        new_dict = self.make_numeric(col, val, col_name_map)
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
        global to_db
        global max_id
        if col == 'notes':
            col_name = 'note_id'
        else:
            col_name = col
        # check if the long_text exists
        sql = 'select id from long_text where long_text = "' + val.replace('"','') + '"'
        long_text = self.to_db.cursor()
        long_text.execute(sql)
        long_text = long_text.fetchone()
        if long_text and long_text[0]:
            return {col_name: long_text[0]}
        if not max_id:
            sql = 'select max(id) from long_text'
            max_id = self.to_db.cursor()
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
        note = to_db.cursor()
        note.execute(sql)
        to_db.commit()
        fk_id = note.lastrowid
        new_dict = {col_name: fk_id}
        return new_dict

    def get_fk_billable(self, col, val, col_name_map):
        if 'SUB' in val:
            new_col = 'order'
        elif 'REA' in val:
            new_col = 'reagent_request'
        else:
            new_col = 'reagent_request'
        fk_id = self.pk_exists(val, 'name', new_col)
        print(val)
        print(fk_id)
        if fk_id:
            if 'SUB' in val:
                new_dict = {'order_id': fk_id}
            elif 'REA' in val:
                new_dict = {'reagent_request_id': fk_id}
            else:
                new_dict = {}
        return new_dict

    def get_fk_user(self, col, val, col_name_map):
        print(col)
        if col in col_name_map:
            col = col_name_map[col]
        if col == 'user':
            val = val.replace(' ','_')
        fk_id = self.pk_exists(val, 'name', col)
        if not fk_id and col == 'user':
            fk_id = self.pk_exists(val, 'email', col)

        if fk_id:
            if col in ['canceler','receiver','requester','orderer', 'pi',
            'owner_institution', 'operator']:
                new_dict = {col: fk_id}
            elif col in col_name_map:
                new_dict = {col_name_map[col]: fk_id}
            else:
                new_dict = {(col + '_id'): fk_id}
        return new_dict

    def limit_val(self, col, val, col_name_map):
        val = val[0:50]
        new_dict = {self.get_col_name(col, col_name_map): val}
        return new_dict

    def get_price_item(self, col, val, col_name_map, organization_id):
        row = self.semantic_select_row(val, 'Sequencing_Price', 'Display_Name',
        'semantic_data')
        price_item_name = row[config.semantic_col_map['value']]
        id_exists = self.pk_exists(price_item_name, 'name', 'price_item')
        return {self.get_col_name(col, col_name_map): id_exists}

    def insert_charge_method(self, item_dict, charge_type):
        charge_id = None
        cm = self.from_db.cursor()
        sql = ("select * from semantic_data where thing = 'Purchase_Order' and name ='" + item_dict['code_name'] + "' and property = 'file'")
        cm.execute(sql)
        cm_row = cm.fetchone()
        file = None
        if cm_row and cm_row[config.semantic_col_map['value']]:
                file = cm_row[config.semantic_col_map['value']]

        name, next_num = self.get_next_name('charge_method')
        row_dict = {
                'name': name,
                'charge_method_type_id': charge_type,
                'organization_id': 1,
                'code': item_dict['code_name'],
                'active': 1,
        }
        if file:
            row_dict['file'] = file
        charge_id = self.do_insert('charge_method', row_dict)
        if charge_id:
            to = self.select_row('table_object',
            {'name':'charge_method'})
            to_id = to[0]
            updated = self.update_row('table_object', {'id':
                to_id}, {'new_name_id': next_num})
        return charge_id

    def migrate_order_charge_method(self, mini_table, thing, new_tbl):
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
        for row_num, row in enumerate(pks_rows):
            pk = row[0]
            if pk in self.get_config('keys_to_skip'):
                continue
            print("\t" + str(row_num) + " Working on name: " + pk)
            sql = "select * from " + mini_table + " where thing = '" + thing + "' and name = '" + pk + "'"
            print(sql)
            item = self.from_db.cursor()
            item.execute(sql)
            item_rows = item.fetchall()
            line_item = {'expense': []}
            item_dict = {}
            for row in item_rows:
                col_name = row[config.semantic_col_map['col_name']]
                val = row[config.semantic_col_map['value']]
                item_dict[col_name] = val
            for i in range(1,5):
                code_name = 'Expense_Code_' + str(i)
                if code_name in item_dict:
                    item_dict['code_name'] = item_dict[code_name]
                    percent_col = 'Expense_Code_Percentage_' + str(i)
                    if percent_col in item_dict:
                        percent = int(item_dict[percent_col].split('.')[0].replace('%', ''))
                    else:
                        percent = 100

                    charge_id = self.pk_exists(item_dict[code_name], 'code',
                            'charge_method')
                    charge_type = 2
                    if ('Charge_Type' in item_dict 
                            and item_dict['Charge_Type'] == 'Purchase_Order'):
                        charge_type = 1
                    if not charge_id:
                        charge_id = self. insert_charge_method(item_dict,
                                charge_type)
                    line_item['expense'].append({'code_name': item_dict[code_name], 'charge_id': charge_id, 'type': 2, 'percent':
                            percent})
            po = None
            if 'Purchase_Order' in item_dict:
                po = item_dict['Purchase_Order']
            if 'Purchase_Order_Number' in item_dict:
                po = item_dict['Purchase_Order_Number']
            if po:
                item_dict['code_name'] = po
                charge_type = 1
                charge_id = self.pk_exists(po, 'code',
                            'charge_method')
                if not charge_id:
                    charge_id = self. insert_charge_method(item_dict,
                            charge_type)
                line_item['expense'].append({'code_name': po, 'charge_id': charge_id, 'type': 1, 'percent':
                        100})
            order_id = None
            if 'Name' in item_dict:
                order_id = self.pk_exists(item_dict['Name'], 'name', 'order')
            print(line_item)
            if order_id:
                for expense in line_item['expense']:
                    name, next_num = self.get_next_name('order_charge_method')
                    cm_dict = {
                        'name': name,
                        'order_id': order_id,
                        'charge_method_id': charge_id,
                        'percent': expense['percent']
                    }
                    print(cm_dict)
                    cm_row = self.do_insert('order_charge_method', cm_dict)
                    if cm_row:
                        to = self.select_row('table_object',
                        {'name':'order_charge_method'})
                        to_id = to[0]
                        updated = self.update_row('table_object', {'id':
                            to_id}, {'new_name_id': next_num})
            print('\tCompleted work on name: ' + pk + "\n\n")
        print('Completed table: ' + mini_table + " thing: " + thing + "\n\n\n\n")
     
    def migrate_user_organization(self, mini_table, thing, new_tbl):
        print("Table: " + mini_table + " thing: " + thing)
        pks = self.from_db.cursor()
        sql = "select distinct name from " + mini_table + " where thing = '" + thing + "'"
        '''sql += " and name in "
        sql += ("('LIN27167','LIN27166','LIN27165','LIN27164','LIN27163','LIN27162','LIN27161','LIN27160','LIN27159','LIN27158','LIN27157','LIN27156','LIN27155','LIN27154','LIN27153','LIN27152','LIN27151','LIN27150','LIN27149','LIN27148','LIN27147','LIN27146','LIN27145','LIN27144','LIN27143','LIN27142','LIN27141','LIN27140','LIN27139','LIN27138','LIN27137','LIN27136','LIN27135','LIN27134','LIN27133','LIN27132','LIN27131','LIN27130','LIN27129','LIN27128','LIN27127','LIN27126','LIN27125','LIN27124','LIN27123','LIN27122','LIN27121','LIN27120','LIN27119','LIN27118','LIN27117','LIN27116','LIN27115','LIN27114','LIN27113','LIN27112','LIN27111','LIN27110','LIN27109','LIN27108','LIN27107','LIN27106','LIN27105','LIN27104','LIN27103','LIN27102','LIN27101','LIN27100','LIN27099','LIN27098','LIN27097','LIN27096','LIN27095','LIN27094','LIN27093','LIN27092','LIN27091','LIN27090','LIN27089','LIN27088','LIN27087','LIN27086','LIN27085','LIN27084','LIN27083','LIN27082','LIN27081','LIN27080','LIN27079')")'''
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
            sql = "select distinct value from " + mini_table + " where thing = '" + thing + "' and property='Group_Member' and name = '" + pk + "'"
            print(sql)
            users = self.from_db.cursor()
            users.execute(sql)
            user_rows = users.fetchall()
            for user in user_rows:
                user_name = user[0]
                user_id = self.pk_exists(user_name, 'name', 'user')
                org_id = self.pk_exists(pk, 'name', 'organization')
                if user_id and org_id:
                    tbl_name = thing
                    print("\t\tMapping data for: " + tbl_name + ' into: ' + new_tbl)
                    row_exists = self.select_row(new_tbl, {'user_id': user_id, 'user_organization_id':org_id}, 1)
                    if row_exists and not no_skip:
                        print("\t\tSkipping because " + pk + " already exists: " +
                                str(row_exists[0]))
                    else:
                        name, next_num = self.get_next_name('user_organization')
                        row_dict = {
                                'name': name,
                                'user_id': user_id,
                                'organization_id': 1,
                                'user_organization_id': org_id,
                                'active': 1,
                                'default_organization': org_id
                        }
                        row = self.do_insert(new_tbl, row_dict)
                        if row:
                            to = self.select_row('table_object',
                            {'name':'user_organization'})
                            to_id = to[0]
                            updated = self.update_row('table_object', {'id':
                                to_id}, {'new_name_id': next_num})

            print('\tCompleted work on name: ' + pk + "\n\n")
        print('Completed table: ' + mini_table + " thing: " + thing + "\n\n\n\n")

    def find_address(self, users, org_id):
        address_set = False
        for u in users:
            sql = "select * from semantic_data where thing = 'Group_Member' and name = '" + u + "'"
            print(sql)
            add_user = self.from_db.cursor()
            add_user.execute(sql)
            add_user_rows = add_user.fetchall()
            address_fields = {
                    'City': 'city',
                    'State': 'state',
                    'Zip': 'postcode',
                    'Postal_Code': 'postcode',
                    'Street_Address': 'address_1',
                    'Country': 'country'
            }
            user_address = {}
            for au_row in add_user_rows:
                if (au_row[2] in address_fields and au_row[3]):
                    user_address[address_fields[au_row[2]]] = au_row[3]
            if user_address:
                row_exists = self.select_row('address', user_address, 1)
                if not row_exists:
                    name, next_num = self.get_next_name('address')
                    row_dict = {
                            'name': name,
                            'organization_id': org_id,
                            'active': 1
                    }
                    print(user_address)
                    row_dict.update(user_address)
                    print(row_dict)
                    row = self.do_insert('address', row_dict)
                    address_id = row
                    if address_id:
                        updated = self.update_row('user', {'name': u}, {'address_id':
                            address_id})
                        address_set = updated
                        print(address_set)
                        updated = self.update_row('table_object', {'name':
                            'address'}, {'new_name_id': next_num})
                        if address_set:
                            break 
                    if address_set:
                        break 
                else:
                    address_id = row_exists[0]
                    print(address_id)
                    updated = self.update_row('user', {'name': u}, {'address_id':address_id})
                    address_set = updated
                    print(address_set)
        if address_set:
            print('success')
        else:
            print('address not set')
        return address_set

    def migrate_address_user(self, mini_table, thing, new_tbl):
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
            print(pk)
            if pk in self.get_config('keys_to_skip'):
                continue
            print("\t" + str(row_num) + " Working on name: " + pk)
            address_set = False
            org_exists = self.select_row('user', {'name': pk, 'address_id': None}, 1)
            org_id = None
            if org_exists:
                org_id = org_exists[6]
            print(org_id)
            if org_id:
                address_set = self.find_address([pk], org_id)
            else:
                print('no org or billing already set')
            print('\tCompleted work on name: ' + pk + "\n\n")
        print('Completed table: ' + mini_table + " thing: " + thing + "\n\n\n\n")

    def migrate_address(self, mini_table, thing, new_tbl):
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
            address_set = False
            org_id = self.pk_exists(pk, 'name', 'organization')
            org_exists = self.select_row('organization', {'name': pk}, 1)
            org_id = None
            billing = None
            if org_exists:
                org_id = org_exists[0]
                billing = org_exists[9]
            print(org_id)
            print(billing)
            if org_id and not billing:
                sql = "select property, value from " + mini_table + " where thing = '" + thing + "' and (property='Lab_Admin' or property ='PI' or 'Group_Member') and name = '" + pk + "'"
                print(sql)
                users = self.from_db.cursor()
                users.execute(sql)
                user_rows = users.fetchall()
                user_types = {}
                for user in user_rows:
                    position = user[0]
                    user_name = user[1]
                    if position not in user_types:
                        user_types[position] = []
                    user_types[position].append(user_name)
                if 'Lab_Admin' in user_types:
                    address_set = self.find_address(user_types['Lab_Admin'], org_id)
                if not address_set and 'PI' in user_types:
                    address_set = self.find_address(user_types['PI'], org_id)
                if not address_set and 'Group_Member' in user_types:
                    address_set = self.find_address(user_types['PI'], org_id)
            else:
                print('no org or billing already set')
            print('\tCompleted work on name: ' + pk + "\n\n")
        print('Completed table: ' + mini_table + " thing: " + thing + "\n\n\n\n")

    def migrate_lab_admins(self, mini_table, thing, new_tbl):
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
            sql = "select property, value from " + mini_table + " where thing = '" + thing + "' and (property='Lab_Admin' or property ='PI') and name = '" + pk + "'"
            print(sql)
            users = self.from_db.cursor()
            users.execute(sql)
            user_rows = users.fetchall()
            for user in user_rows:
                position = user[0]
                user_name = user[1]
                print(user_name)
                print(position)
                if position == 'Lab_Admin':
                    position = 'manager'
                org_id = self.pk_exists(pk, 'name', 'organization')
                user_id = self.pk_exists(user_name, 'name', 'user')
                if org_id and not user_id:
                    sql = "select * from " + mini_table + " where thing = 'Group_Member' and name = '" + user_name + "'"
                    print(sql)
                    add_user = self.from_db.cursor()
                    add_user.execute(sql)
                    add_user_rows = add_user.fetchall()
                    email = user_name
                    for au_row in add_user_rows:
                        print(au_row)
                        if au_row[2] == 'Email':
                            if au_row[3]:
                                email = au_row[3]
                            break
                    row_dict = {
                            'email': email,
                            'name': user_name,
                            'organization_id': org_id,
                            'active': 1
                    }
                    row = self.do_insert('user', row_dict)
                    user_id = row
                pos_id = self.pk_exists(position, 'name', 'position')
                if user_id and org_id and pos_id:
                    tbl_name = thing
                    print("\t\tMapping data for: " + tbl_name + ' into: ' + new_tbl)
                    row_exists = self.select_row('user_organization', {'user_id': user_id, 'user_organization_id':org_id}, 1)
                    if row_exists:
                        user_org_id = row_exists[0]
                    else:
                        row_dict = {
                                'name': 'user_' + pk + '_' + user_name,
                                'user_organization_id': org_id,
                                'user_id': user_id,
                                'organization_id': 1,
                                'active': 1
                        }
                        row = self.do_insert('user_organization', row_dict)
                        if row:
                            user_org_id = row
                    if user_org_id:
                        row_exists = self.select_row('user_organization_position', {'position_id': pos_id, 'user_organization_id':user_org_id}, 1)
                        if row_exists and not no_skip:
                            print("\t\tSkipping because " + pk + " already exists: " +
                                    str(row_exists[0]))

                        else:
                            name, next_num = self.get_next_name('user_organization_position')
                            row_dict = {
                                    'name': name,
                                    'user_organization_id': user_org_id,
                                    'organization_id': 1,
                                    'active': 1,
                                    'position_id': pos_id
                            }
                            row = self.do_insert(new_tbl, row_dict)
                            if row:
                                to = self.select_row('table_object',
                                {'name':'user_organization_position'})
                                to_id = to[0]
                                updated = self.update_row('table_object', {'id':
                                    to_id}, {'new_name_id': next_num})
                    else:
                        print('\tUser_Organization Does not exist: ' + pk + "\n\n")
            
                else:
                    print('\tUser_id, Org_id or Pos_id Does not exist: ' + pk + "\n\n")
                    print(user_id)
                    print(org_id)
                    print(pos_id)
            print('\tCompleted work on name: ' + pk + "\n\n")
        print('Completed table: ' + mini_table + " thing: " + thing + "\n\n\n\n")




    def parse_cli(self):
        cli = super(MigrateCustomScript, self).parse_cli()
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
        self.migrate_address_user(self.cli['semantic_source'], self.cli['from_tbl'], self.cli['to_tbl'])

# execute run on this class
script = MigrateCustomScript()
script.run()
