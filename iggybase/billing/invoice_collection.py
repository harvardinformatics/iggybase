from flask import render_template, current_app, url_for, request
from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta
from iggybase import g_helper
from iggybase.core.table_query import TableQuery
from iggybase import utilities as util
from .invoice import Invoice
from flask_weasyprint import render_pdf, HTML
import logging

class InvoiceCollection:
    # either a table_name or a table_query_id must be supplied
    def __init__ (self, year = None, month = None, org_name = None):
        last_month = datetime.datetime.now() + relativedelta(months=-1)
        if not year:
            year = last_month.year
        if not month:
            month = last_month.month
        self.month = month
        self.year = year
        self.from_date, self.to_date = self.parse_dates()
        self.month_str = self.from_date.strftime('%b')
        self.org_name = org_name
        self.oac = g_helper.get_org_access_control()
        self.invoices = self.get_invoices(self.from_date, self.to_date, self.org_name)
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
        self.set_invoices()

    def parse_dates(self):
        from_date = datetime.date(year=self.year, month=self.month, day=1)
        to_date = from_date + relativedelta(months=1) - relativedelta(days=1)
        return from_date, to_date

    def get_invoices(self, from_date, to_date, org_name = None):
        invoices = {} # line_items by org_id
        res = self.oac.get_line_items(from_date, to_date, org_name)
        item_dict = {}
        for row in res:
            org_name = row.Organization.name
            if org_name in item_dict:
                item_dict[org_name].append(row)
            else:
                item_dict[org_name] = [row]
        for org_name, item_list in item_dict.items():
            invoices[org_name] = Invoice(self.from_date, self.to_date, org_name, item_list)
        return invoices

    def get_table_query(self, table):
        self.table_query = TableQuery(None, 1, table, table,
                self.table_query_criteria[table])

    def set_invoices(self):
        for invoice in self.invoices.values():
            if invoice.total:
                invoice.set_invoice()

    def update_pdf_names(self):
        for invoice in self.invoices.values():
            if invoice.total:
                invoice.update_pdf_name()

    def generate_pdfs(self):
        generated = []
        for invoice in self.invoices.values():
            if invoice.total:
                path = self.generate_pdf(invoice)
                if path:
                    generated.append(path)
        return generated

    def populate_tables(self):
        for invoice in self.invoices.values():
            invoice.populate_tables()

    def get_select_options(self):
        self.select_years = util.get_last_x_years(5)
        self.select_months = util.get_months_dict()

    def generate_pdf(self, invoice):
        try:
            html = render_template('invoice_base.html',
            module_name = 'billing',
            invoice = invoice)
            path = invoice.get_pdf_path()
            #HTML(url_for('billing.invoice', facility_name = 'bauer', year=2016, month=5,
            #    org_name = 'Bauer_Core')).write_pdf(url)
            HTML(string=html).write_pdf(path)
            return path
        except:
            return False

    def get_invoice_by_org(self, org_name):
        first = None
        if org_name in self.invoices:
            first = self.invoices[org_name]
        return first
