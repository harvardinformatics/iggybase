from flask import render_template, request, g
from collections import OrderedDict, defaultdict
import datetime, re
from iggybase import g_helper
from iggybase import utilities as util
from flask_weasyprint import HTML
import logging
import os

class LineItemCollection:
    def __init__ (self, year = None, month = None, org_list = [], invoiced =
            False):
        # default to last month
        last_month = util.get_last_month()
        if not year:
            year = last_month.year
        if not month:
            month = last_month.month

        self.month = month
        self.year = year
        self.org_list = org_list
        self.invoiced = invoiced
        self.from_date, self.to_date = util.start_and_end_month(self.year,
                self.month)
        self.reports = OrderedDict()



        self.oac = g_helper.get_org_access_control()
        self.line_items = self.oac.get_line_items(self.from_date, self.to_date, self.org_list,
                self.invoiced)

    def group_line_items(self, key_types, data_types, criteria = None):
        # group by (org_name, 'code') for codes or (org_name, charge_method) for po
        # set invoice_order
        item_dict = OrderedDict()
        for row in self.line_items:
            if criteria:
                if getattr(getattr(row, criteria['table']), criteria['field']) == criteria['value']:
                    # calculate key values for this row
                    keys = [getattr(self, x['func'])(x, row) for x in key_types]
                    item_dict = self.group_row(item_dict, 0, keys, data_types, row)
            else:
                # calculate key values for this row
                keys = [getattr(self, x['func'])(x, row) for x in key_types]
                item_dict = self.group_row(item_dict, 0, keys, data_types, row)
        return item_dict

    def group_row(self, item_dict, index, keys, data_types, row):
        while(index < len(keys)):
            key_val = keys[index]
            index += 1
            if key_val not in item_dict:
                item_dict[key_val] = defaultdict()
            val = self.group_row(item_dict[key_val], index, keys, data_types,
                    row)
            item_dict[key_val] = val
            return item_dict
        if not item_dict:
            item_dict = OrderedDict()
        # append any data to the group
        for data in data_types:
            if 'per_row' in data and data['per_row']:
                item_dict[data['key']] = getattr(self, data['func'])(data, row,
                        item_dict.get(data['key'], None))
            else:
                if data['key'] not in item_dict:
                    item_dict[data['key']] = getattr(self, data['func'])(data, row)
        # return the data which will be set to the dict with nested grouping
        return item_dict

    def populate_report_data(self):
        # TODO: consider a report class
        # and how line items and invoices relate
        self.populate_item_report()
        self.populate_department_report()
        self.populate_user_report()
        self.populate_code_report()
        self.populate_po_report()

    def populate_item_report(self):
        key_types = [
                {
                    'func':'get_table_col',
                    'fields':{'PriceItem': 'name'}
                }
        ]
        data_types = [
                {
                    'key':'group type',
                    'func':'get_table_col',
                    'fields':{'OrganizationType': 'name'}
                },
                {
                    'key':'analysis type',
                    'func':'get_table_col',
                    'fields':{'PriceItem': 'name'}
                },
                {
                    'key':'cost',
                    'per_row':True,
                    'func':'sum_charges'
                },
                {
                    'key':'quantity',
                    'per_row':True,
                    'func':'sum_quantity'
                }
        ]
        group_by = self.group_line_items(key_types, data_types)
        self.reports['Monthly Usage'] = list(group_by.values())

    def populate_department_report(self):
        key_types = [
                {
                    'func':'get_table_col',
                    'fields':{'Department': 'name', 'PriceItem': 'name'}
                }
        ]
        data_types = [
                {
                    'key':'group type',
                    'func':'get_table_col',
                    'fields':{'OrganizationType': 'name'}
                },
                {
                    'key':'analysis type',
                    'func':'get_table_col',
                    'fields':{'PriceItem': 'name'}
                },
                {
                    'key':'department',
                    'func':'get_table_col',
                    'fields':{'Department': 'name'}
                },
                {
                    'key':'cost',
                    'per_row':True,
                    'func':'sum_charges'
                },
                {
                    'key':'quantity',
                    'per_row':True,
                    'func':'sum_quantity'
                }
        ]
        group_by = self.group_line_items(key_types, data_types)
        self.reports['Department Monthly Usage'] = list(group_by.values())

    def populate_user_report(self):
        key_types = [
                {
                    'func':'get_table_col',
                    'fields':{'Organization': 'name','User': 'name'}
                }
        ]
        data_types = [
                {
                    'key':'group',
                    'func':'get_table_col',
                    'fields':{'Organization': 'name'}
                },
                {
                    'key':'user',
                    'func':'get_table_col',
                    'fields':{'User': 'name'}
                },
                {
                    'key':'institution',
                    'func':'get_table_col',
                    'fields':{'Institution': 'name'}
                },
                {
                    'key':'department',
                    'func':'get_table_col',
                    'fields':{'Department': 'name'}
                },
                {
                    'key':'email',
                    'func':'get_table_col',
                    'fields':{'User': 'email'}
                },
                {
                    'key':'cost',
                    'per_row':True,
                    'func':'sum_charges'
                },
                {
                    'key':'quantity',
                    'per_row':True,
                    'func':'sum_quantity'
                }
        ]
        group_by = self.group_line_items(key_types, data_types)
        self.reports['User Monthly Usage'] = list(group_by.values())

    def populate_code_report(self):
        key_types = [
                {
                    'func':'get_table_col',
                    'fields':{'ChargeMethod': 'code'}
                }
        ]
        data_types = [
                {
                    'key':'total',
                    'per_row':True,
                    'func':'sum_charges'
                },
                {
                    'key':'split_code',
                    'func':'split_code'
                },
                {
                    'key':'invoice',
                    'func':'get_invoice_pdf',
                    'per_row':True
                }
        ]
        group_by = self.group_line_items(key_types, data_types,
                {'table':'ChargeMethodType', 'field':'name', 'value':'code'})
        self.reports['Expense Code Monthly Usage'] = self.format_code_report(group_by)

    def populate_po_report(self):
        key_types = [
                {
                    'func':'get_table_col',
                    'fields':{'ChargeMethod': 'code'}
                }
        ]
        data_types = [
                {
                    'key':'purchase order',
                    'func':'get_table_col',
                    'fields':{'ChargeMethod': 'code'}
                },
                {
                    'key':'total',
                    'per_row':True,
                    'func':'sum_charges'
                },
                {
                    'key':'original',
                    'func':'get_table_col',
                    'fields':{'ChargeMethod': 'original_value'}
                },
                {
                    'key':'remaining',
                    'func':'get_table_col',
                    'fields':{'ChargeMethod': 'remaining_value'}
                },
                {
                    'key':'invoice',
                    'func':'get_invoice_pdf',
                    'per_row':True
                }
        ]
        group_by = self.group_line_items(key_types, data_types,
                {'table':'ChargeMethodType', 'field':'name', 'value':'po'})
        self.reports['Purchase Order Monthly Usage'] = list(group_by.values())


    def format_code_report(self, group):
        tbl = []
        for item in group.values():
            row = item['split_code']
            row['Total Cost'] = item['total']
            row['Invoice'] = item['invoice']
            tbl.append(row)
        return tbl



    ''' Group functions below '''

    def get_table_col(self, x, row):
        val = x.get('default', '')
        # can be a compound of multiple fields
        for table_object, field in x['fields'].items():
            val += str(getattr(getattr(row, table_object, None),
                            field, None))
        return val

    def item_list(self, x, row, curr_val = None):
        if curr_val == None:
            curr_val = []
        curr_val.append(row)
        return curr_val

    def sum_charges(self, x, row, curr_val = None):
        total = curr_val or 0
        total += (float(row.LineItem.price_per_unit) * row.LineItem.quantity *
                (row.OrderChargeMethod.percent/100))
        return total

    def sum_quantity(self, x, row, curr_val = None):
        total = curr_val or 0
        total += row.LineItem.quantity
        return total

    def split_code (self, x, row):
        split_code = OrderedDict()
        code_parts = ['Tub', 'Org', 'Object', 'Fund', 'Activity', 'Sub-activity', 'Root']
        clean_code = util.clean_billing_code(row.ChargeMethod.code)
        code_arr = clean_code.split('-')
        code_arr_len = len(code_arr)
        for i, part in enumerate(code_parts):
            split_code[part] = None
            if i < code_arr_len:
                split_code[part] = code_arr[i]
        return split_code

    def get_invoice_pdf(self, x, row, curr_val = None):
        if curr_val == None:
            curr_val = []
        curr_val.append(row.Invoice.pdf)
        return curr_val
