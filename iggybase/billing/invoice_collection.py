from flask import render_template, request, g
from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta
from iggybase import g_helper
from iggybase.core.table_query import TableQuery
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

        self.oac = g_helper.get_org_access_control()
        # create invoice objects
        self.invoices = self.get_invoices(self.from_date, self.to_date, self.org_list)
        self.populate_tables()
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
        for row in res:
            org_name = row.Organization.name
            if org_name in item_dict:
                item_dict[org_name].append(row)
            else:
                item_dict[org_name] = [row]
        for order, item_list in enumerate(item_dict.values()):
            invoices.append(Invoice(self.from_date, self.to_date, org_name, item_list, order))
        return invoices

    def get_table_query(self, table):
        self.table_query = TableQuery(None, 1, table, table,
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
        try:
            html = render_template('invoice_base.html',
            module_name = 'billing',
            invoices = [invoice])
            path = invoice.get_pdf_path()
            HTML(string=html).write_pdf(path)
            return path
        except:
            return False

    def populate_tables(self):
        for invoice in self.invoices:
            invoice.populate_tables()

    def get_select_options(self):
        self.select_years = util.get_last_x_years(5)
        self.select_months = util.get_months_dict()

    def get_all_pdf_name(self):
        return 'invoice-' + str(self.from_date.year) + '-' + '{:02d}'.format(self.from_date.month) + '.pdf'

    def get_all_pdf_link(self):
        link = request.url_root + g.facility + '/billing/invoice/' + self.get_all_pdf_name()
        return link
