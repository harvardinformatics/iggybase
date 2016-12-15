from flask import render_template, request, g
from collections import OrderedDict, defaultdict
import datetime
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

        self.oac = g_helper.get_org_access_control()
        self.line_items = self.oac.get_line_items(self.from_date, self.to_date, self.org_list,
                self.invoiced)

    def group_line_items(self, key_types, data_types):
        # group by (org_name, 'code') for codes or (org_name, charge_method) for pos
        # set invoice_order
        item_dict = OrderedDict()
        for row in self.line_items:
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
            item_dict = defaultdict()
        # append any data to the group
        for data in data_types:
            if 'format' in data and data['format'] == 'list':
                if data['key'] not in item_dict:
                    item_dict[data['key']] = []
                item_dict[data['key']].append(row)
            else:
                if data['key'] not in item_dict:
                    item_dict[data['key']] = getattr(self, data['func'])(data, row)
        # return the data which will be set to the dict with nested grouping
        return item_dict

    def get_table_col(self, x, row):
        return getattr(getattr(row, x['table_object']),
                            x['field'])

    def populate_report_data(self):
        self.report = self.group_line_items('expense_code')

