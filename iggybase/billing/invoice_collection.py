from flask import render_template, request, g
from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta
from iggybase import g_helper
from iggybase.core.table_query_collection import TableQueryCollection
from iggybase import utilities as util
from .invoice import Invoice
from flask_weasyprint import HTML
import logging
import os

class InvoiceCollection:
    def __init__ (self, year = None, month = None, org_list = []):
        # default to last month
        last_month = datetime.datetime.now() + relativedelta(months=-1)
        if not year:
            year = last_month.year
        if not month:
            month = last_month.month

        self.month = month
        self.year = year
        self.org_list = org_list
        self.from_date, self.to_date = self.parse_dates()
        self.month_str = self.from_date.strftime('%b')

        # create invoice objects
        self.oac = g_helper.get_org_access_control()
        self.invoices = self.get_invoices(self.from_date, self.to_date, self.org_list)

        # used when making table queries
        self.table_query_criteria = {
                'line_item': {
                    ('line_item', 'date_created'): {'from': self.from_date, 'to': self.to_date},
                    ('line_item', 'price_per_unit'): {'compare': 'greater than',
                        'value': 0}
                },
                'invoice': {
                    ('invoice', 'invoice_month'): {'from': self.from_date, 'to': self.to_date},
                }
        }

        self.set_invoices() # creates invoice rows in DB

    def parse_dates(self):
        from_date = datetime.date(year=self.year, month=self.month, day=1)
        to_date = from_date + relativedelta(months=1) - relativedelta(days=1)
        return from_date, to_date

    def get_invoices(self, from_date, to_date, org_list = []):
        invoices = []
        res = self.oac.get_line_items(from_date, to_date, org_list)
        item_dict = OrderedDict()
        # group by (org_name, 'code') for codes or (org_name, charge_method) for pos
        # set invoice_order
        for row in res:
            # set service_type as level of grouping for invoice within facility
            service_prefix = row.ServiceType.invoice_prefix
            service_type_id = row.ServiceType.id
            if not service_prefix in item_dict:
                item_dict[service_prefix] = {}
            org_name = row.Organization.name
            if row.ChargeMethodType.name == 'code':
                charge_method = 'code'
            else:
                charge_method = row.ChargeMethod.name
            key = (row.Organization.name, charge_method)
            if key in item_dict[service_prefix]:
                item_dict[service_prefix][key]['items'].append(row)
                if not item_dict[service_prefix][key]['invoice_order']:
                    inv = getattr(row, 'Invoice', None)
                    if inv:
                        item_dict[service_prefix][key]['invoice_order'] = inv.order
            else:
                item_dict[service_prefix][key] = {
                        'invoice_order': None,
                        'items': [row],
                        'service_type_id': service_type_id
                }
                inv = getattr(row, 'Invoice', None)
                if inv:
                    item_dict[service_prefix][key]['invoice_order'] = inv.order
        # we need to order by org_name but if recreated we need to keep the old
        # order
        new_invoices = {}
        max_invoice_order = 0
        # set existing invoices first, maintaining order
        for service_prefix, items in item_dict.items():
            for item_list in items.values():
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
                else:
                    new_invoices[service_prefix] = item_list
        # then set new invoices in order of org_name
        # increasing order after existing invoices
        for service_prefix, new_invoice in new_invoices.items():
            invoices.append(
                    Invoice(
                        self.from_date,
                        self.to_date,
                        new_invoice['items'],
                        (max_invoice_order + 1),
                        service_prefix,
                        new_invoice['service_type_id']
                    )
            )
            max_invoice_order += 1
        return invoices

    def get_table_query_collection(self, table):
        self.tqc = TableQueryCollection(table,
                self.table_query_criteria[table])

    def set_invoices(self):
        for invoice in self.invoices:
            if invoice.total:
                invoice.set_invoice()

    def update_pdf_names(self):
        for invoice in self.invoices:
            if invoice.total:
                invoice.update_pdf_name()

    def generate_pdfs(self):
        generated = []
        for invoice in self.invoices:
            if invoice.total:
                path = self.generate_pdf(invoice)
                if path:
                    generated.append(path)
        return generated

    def generate_pdf(self, invoice):
        html = render_template('invoice_base.html',
        module_name = 'billing',
        invoices = [invoice])
        path = invoice.get_pdf_path()
        HTML(string=html).write_pdf(path)
        return path

    def populate_template_data(self):
        for invoice in self.invoices:
            invoice.populate_template_data()

    def get_select_options(self):
        self.select_years = util.get_last_x_years(5)
        self.select_months = util.get_months_dict()

    def get_all_pdf_name(self):
        return 'invoice-' + str(self.from_date.year) + '-' + '{:02d}'.format(self.from_date.month) + '.pdf'

    def get_all_pdf_link(self):
        link = request.url_root + g.facility + '/billing/invoice/' + self.get_all_pdf_name()
        return link
