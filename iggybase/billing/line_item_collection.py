from flask import render_template, request, g
from collections import OrderedDict
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

    def group_line_items(self, res):
        # group by (org_name, 'code') for codes or (org_name, charge_method) for pos
        # set invoice_order
        item_dict = OrderedDict()
        for row in res:
            # set service_type as level of grouping for invoice within facility
            service_prefix = row.ServiceType.invoice_prefix
            service_type_id = row.ServiceType.id
            if not service_prefix in item_dict:
                item_dict[service_prefix] = {}
            key = self.org_charge_tuple(row)
            if key in item_dict[service_prefix]:
                item_dict[service_prefix][key]['items'].append(row)
                # if key exists and order not yet set then try to set or stay None
                if not item_dict[service_prefix][key]['invoice_order']:
                    item_dict[service_prefix][key]['invoice_order'] = self.check_invoice_order(row)
            else:
                item_dict[service_prefix][key] = {
                        'invoice_order': None,
                        'items': [row],
                        'service_type_id': service_type_id
                }
                item_dict[service_prefix][key]['invoice_order'] = self.check_invoice_order(row)
        return item_dict

    def org_charge_tuple(self, row):
        ''' creates tuple from Org name, charge method
        if method is PO then uses number, for code uses
        'code' so that they are all on same invoice '''
        org_name = row.Organization.name
        if row.ChargeMethodType.name == 'code':
            charge_method = 'code'
        else:
            charge_method = row.ChargeMethod.name
        return (row.Organization.name, charge_method)

    def check_invoice_order(self, row):
        ''' if invoice has an invoice_order return otherwise None'''
        inv = getattr(row, 'Invoice', None)
        if inv and hasattr(inv, 'invoice_number'):
            return inv.invoice_number
        return None

    def populate_report_data(self):
        self.report = self.group_line_items('expense_code')

