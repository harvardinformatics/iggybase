import sys
import os

# add iggybase root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import datetime
import re
import json
from dateutil.relativedelta import relativedelta
import glob
from xml.etree import ElementTree
import csv
from scripts.iggy_script import IggyScript
#import insert_config as config

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

class MetadataScript (IggyScript):
    def __init__(self):
        super(MetadataScript, self).__init__()

    def insert_row(self, tbl, cols):
        col_val_map = self.get_map(tbl, 'col_value')
        cols.update(col_val_map)
        id = None
        if cols:
            fields = {}
            sql = 'insert into ' + tbl
            for key, val in cols.items():
                if 'func_' in str(val):
                    func_name = val.replace('func_', '')
                    if func_name in globals():
                        criteria['insert_table'] = tbl
                        fields[key] = globals()[func_name](key, criteria)
                    else:
                        print('Error, no function ' + func_name + 'defined')
                        sys.exit(1)
                else:
                    fields[key] = val
            id = self.do_insert(tbl, fields)
        return id

    def insert_metadata(self, table_name, new_name_prefix, role_list, order):
        print("Starting on Table: " + table_name + ' and role_list: ' +
                json.dumps(role_list))
        print("\tCheck for Table: " + table_name)
        table_object = self.select_row('table_object', {'name': table_name})
        if table_object:
            table_object_id = table_object[0]
            print("\tTable found, id: " + str(table_object_id))
        else:
            print("\tTable not found, inserting: " + table_name)
            cols = {'name': table_name, 'new_name_prefix': new_name_prefix,
                    'order':order}
            table_object_id = self.insert_row('table_object', cols)
            if table_object_id:
                print("\tTable inserted: " + table_name + " has id: " +
                        str(table_object_id))
            else:
                print("Table NOT inserted, ABORTING: " + table_name)
                return False
        self.add_roles('table_object', table_object_id, role_list)
        print("\tTry to get Fields")
        fields = self.show_cols(table_name)
        for i, field in enumerate(fields):
            if field:
                col = field[0]
                print("\t\tCheck Field: " + col)
                field_row = self.select_row('field', {'display_name': col,
                    'table_object_id':table_object_id})
                if field_row:
                    field_id = field_row[0]
                    print("\t\tField found: " + str(field_id))
                    self.add_roles('field', field_id, role_list)
                else:
                    print("\t\tField not found, inserting")
                    type_map = {
                            'int':1,
                            'varchar':2,
                            'tinyint':3,
                            'datetime':4,
                            'decimal':9,
                            'float':10
                    }
                    f_name, f_next_num = self.get_next_name('field')
                    order = i
                    data = re.split('[\(\)]', field[1])
                    data_type_id = type_map[data[0]]
                    unique = 0
                    pk = 0
                    if field[3] == 'PRI':
                        pk = 1
                    elif field[3] == 'UNI':
                        unique = 1
                    field_cols = {'table_object_id': table_object_id, 'display_name': col,
                            'name': f_name, 'order': order,
                            'data_type_id':data_type_id, 'unique':unique, 'primary_key':pk}

                    if data_type_id != 4 and 1 in data:
                        field_cols['length'] = data[1]
                    foreign_key_table_object_id = None
                    foreign_key_field_id = None
                    if '_id' in col:
                        fk_tbl = col.split('_id')[0]
                        fk_table_object = self.select_row('table_object', {'name': fk_tbl})
                        if fk_table_object:
                            foreign_key_table_object_id = fk_table_object[0]
                            fk_field = self.select_row('field', {'table_object_id':
                                foreign_key_table_object_id, 'display_name':'id'})
                            if fk_field:
                                foreign_key_field_id = fk_field[0]
                    if foreign_key_table_object_id:
                        field_cols['foreign_key_table_object_id'] = foreign_key_table_object_id
                    if foreign_key_field_id:
                        field_cols['foreign_key_field_id'] = foreign_key_field_id
                    field_id = self.insert_row('field', field_cols)
                    if field_id:
                        print("\tField inserted: " + str(field_id))
                        field_to = self.select_row('table_object',
                        {'name':'field'})
                        field_to_id = field_to[0]
                        updated = self.update_row('table_object', {'id':
                            field_to_id}, {'new_name_id': f_next_num})
                        self.add_roles('field', field_id, role_list)
                    else:
                        print("\tField NOT inserted: " + str(col))

        print("Completed Table: " + table_name + "\n\n\n")

    def add_roles(self, tbl_name, tbl_id, role_list):
        print("\tCheck for " + tbl_name + "Role: " + json.dumps(role_list))
        for role in role_list:
            print("\tCheck for Role: " + str(role))
            table_object_role = self.select_row((tbl_name + '_role'), {(tbl_name + '_id'):
                tbl_id, 'role_id':role})
            if table_object_role:
                table_object_role_id = table_object_role[0]
                print("\t" + tbl_name + "Role found, id: " + str(table_object_role_id))
            else:
                print("\t" + tbl_name + "Role not found, inserting: " + str(role))
                name, next_num = self.get_next_name((tbl_name + '_role'))
                cols = {(tbl_name + '_id'): tbl_id, 'role_id': role, 'name':
                        name}
                table_object_role_id = self.insert_row((tbl_name + '_role'), cols)
                if table_object_role_id:
                    print("\t" + tbl_name + "Role inserted: " + str(table_object_role_id))
                    role_to = self.select_row('table_object',
                    {'name':(tbl_name + '_role')})
                    role_to_id = role_to[0]
                    updated = self.update_row('table_object', {'id':
                        role_to_id}, {'new_name_id': next_num})
                else:
                    print(tbl_name + "Role NOT inserted: " + str(role))

    def show_cols(self, tbl):
        pks = self.db.cursor()
        sql = "show columns from `" + tbl + "`"
        print("\t\t" + sql)
        pks.execute(sql)
        pks_row = pks.fetchall()
        print(pks_row)
        return pks_row

    def run(self):
        #insert_metadata('unit', 'U', [1, 63])
        #insert_metadata('reagent', 'R', [1, 63])
        #insert_metadata('illumina_adapter', 'R', [1, 63])
        #insert_metadata('sequencing_price', 'SP', [1, 63])
        #insert_metadata('project', 'PR', [1, 63])
        #insert_metadata('invoice_template', 'IT', [1, 63])
        #self.insert_metadata('machine', 'MN', [1, 63], 2)
        #insert_metadata('purchase_order', 'PO', [1, 63])
        #insert_metadata('line_item', 'LI', [1, 63])
        #insert_metadata('illumina_bclconversion_analysis', 'BCL', [1, 63])
        #insert_metadata('illumina_run', 'IR', [1, 63])
        #insert_metadata('sample', 'SA', [1, 63])
        #insert_metadata('sample_sheet', 'SS', [1, 63])
        #insert_metadata('reagent_request', 'RR', [1, 63], 31)
        #insert_metadata('illumina_flowcell', 'IF', [1, 63], 32)
        #self.insert_metadata('invoice', 'IV', [1, 63], 33)
        #insert_metadata('charge_method_type', 'CMT', [1, 63], 34)
        self.insert_metadata('charge_method', 'CM', [1, 63], 35)
        #insert_metadata('invoice_item', 'II', [1, 63], 36)
        #insert_metadata('invoice_template', 'IT', [1, 63], 37)
        #insert_metadata('order_charge_method', 'OCM', [1, 63], 38)
        #insert_metadata('price_category', 'PC', [1, 63], 39)
        #insert_metadata('price_list', 'PL', [1, 63], 40)
        #insert_metadata('sample_sheet_item', 'SI', [1, 63], 41)
        #insert_metadata('select_list', 'SL', [1, 63], 42)
        #insert_metadata('select_list_item', 'SLI', [1, 63], 43)
        #insert_metadata('transaction_type', 'TT', [1, 63], 45)
        #insert_metadata('price_list', 'PL', [1, 63], 41)
        #self.insert_metadata('price_item', 'PI', [1, 63], 40)
        #insert_metadata('price_type', 'PT', [1, 63], 39)
        #self.insert_metadata('line_item', 'LI', [1, 63], 41)
        #self.insert_metadata('lane', 'LN', [1, 63], 42)
        #self.insert_metadata('illumina_run', 'IR', [1, 63], 42)
        #self.insert_metadata('line_item_assoc', 'LA', [1, 63], 43)
        #self.insert_metadata('sequencing_price', 'SP', [1, 63], 45)
        #self.insert_metadata('read', 'RD', [1, 63], 46)
        #self.insert_metadata('price_item_assoc', 'PA', [1, 63], 47)
        #self.insert_metadata('machine_type', 'MT', [1, 63], 1)
        #self.insert_metadata('service_type', 'ST', [1, 63], 1)
        #self.insert_metadata('user_organization_position', 'UP', [1, 63], 48)

script = MetadataScript()
script.run()
