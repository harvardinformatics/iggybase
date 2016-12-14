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
        self.invoices = self.get_invoices(self.from_date, self.to_date, self.org_list)
        self.set_invoices() # creates invoice rows in DB

    def get_invoices(self, from_date, to_date, org_list = []):
        invoices = []
        # group line items by group and service_type as well as "code" or PO
        item_dict = self.group_line_items(self.line_items)
        # we need to order by org_name but if recreated we need to keep the old
        # order
        new_invoices = {}
        max_invoice_order = 0
        # set existing invoices first, maintaining order
        for service_prefix, groups in item_dict.items():
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

    def set_invoices(self):
        for invoice in self.invoices:
            invoice.set_invoice()

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
