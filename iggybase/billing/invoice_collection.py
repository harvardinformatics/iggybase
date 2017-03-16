from flask import render_template, request, g
from collections import OrderedDict
import datetime
from iggybase import g_helper
from iggybase import utilities as util
from .line_item_collection import LineItemCollection
from .invoice import Invoice
from flask_weasyprint import HTML
import logging
import os

class InvoiceCollection(LineItemCollection):
    def __init__ (self, year = None, month = None, org_list = [], invoiced =
            False):
        super(InvoiceCollection, self).__init__(year, month, org_list, invoiced)
        # keys and data needed for grouping line items
        key_types = [
                {
                    'func':'get_table_col',
                    'fields':{'ServiceType': 'invoice_prefix'},
                    'default': 'service'
                },
                {
                    'func':'org_charge_tuple'
                }
        ]
        data_types = [
                {
                    'key':'items',
                    'func':'item_list',
                    'per_row':True
                },
                {
                    'func':'check_invoice_order',
                    'key':'invoice_order'
                },
                {
                    'func':'get_table_col',
                    'fields':{'ServiceType': 'id'},
                    'key':'service_type_id'
                }
        ]
        # group line items by group and service_type as well as "code" or PO
        self.item_dict = self.group_line_items(key_types, data_types)
        self.invoices = self.get_invoices(self.from_date, self.to_date, self.org_list)
        self.set_invoices() # creates invoice rows in DB
        self.invoices.sort(key=lambda x: x.order) # sort by number
        self.total = self.get_total()
        self.display_total = util.format_money(self.total)

    def get_invoices(self, from_date, to_date, org_list = []):
        invoices = []
        # we need to order by org_name but if recreated we need to keep the old
        # order
        new_invoices = {}
        max_invoice_order = 0
        # set existing invoices first, maintaining order
        for service_prefix, groups in self.item_dict.items():
            for group, item_list in groups.items():
                if item_list['invoice_order']:
                    invoice_order = item_list['invoice_order']
                    invoices.append(
                            Invoice(
                                self.from_date,
                                self.to_date,
                                item_list['items'],
                                invoice_order,
                                service_prefix,
                                item_list['service_type_id']
                            )
                    )
                    if invoice_order > max_invoice_order:
                        max_invoice_order = invoice_order
                else: # only new invoices will not have an order
                    if service_prefix not in new_invoices:
                        new_invoices[service_prefix] = {}
                    new_invoices[service_prefix][group] = item_list

        # then set new invoices in order of org_name
        # increasing order after existing invoices
        for service_prefix, groups in new_invoices.items():
            for group, item_list in groups.items():
                new_invoice_num = max_invoice_order + 1
                invoices.append(
                        Invoice(
                            self.from_date,
                            self.to_date,
                            item_list['items'],
                            new_invoice_num,
                            service_prefix,
                            item_list['service_type_id']
                        )
                )
                max_invoice_order = new_invoice_num
        return invoices

    def get_total(self):
        total = 0
        for inv in self.invoices:
            total += inv.total
        return total

    def org_charge_tuple(self, x, row):
        # creates tuple from Org name, charge method
        # if method is PO then uses number, for code uses
        # 'code' so that they are all on same invoice
        org_name = row.Organization.name
        if row.ChargeMethodType.name == 'code':
            charge_method = 'code'
        else:
            charge_method = row.ChargeMethod.name
        return (row.Organization.name, charge_method)

    def check_invoice_order(self, x, row):
        # if invoice has an invoice_order return otherwise None
        inv = getattr(row, 'Invoice', None)
        if inv and hasattr(inv, 'invoice_number'):
            return inv.invoice_number
        return None

    def set_invoices(self):
        single_group = False
        if self.org_list:
            single_group = True
        for invoice in self.invoices:
            invoice.set_invoice(single_group)

    def update_pdf_names(self):
        for invoice in self.invoices:
            if invoice.total:
                invoice.update_pdf_name()

    def generate_pdfs(self):
        generated = []
        # don't regenerate invoices from old system
        old_invoice_date = datetime.date(year=2016, month=8, day=1)
        for invoice in self.invoices:
            if invoice.from_date > old_invoice_date:
                if invoice.total:
                    path = self.generate_pdf(invoice)
                    if path:
                        generated.append(path)
        return generated

    def generate_pdf(self, invoice):
        # don't regenerate invoices from old system
        old_invoice_date = datetime.date(year=2016, month=8, day=1)
        if invoice.from_date > old_invoice_date:
            html = render_template('invoice_base.html',
            module_name = 'billing',
            invoices = [invoice])
            path = invoice.get_pdf_path()
            HTML(string=html).write_pdf(path)
            return path
        else:
            return None

    def populate_template_data(self):
        for invoice in self.invoices:
            invoice.populate_template_data()
