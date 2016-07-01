from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta
from iggybase import g_helper
from iggybase.core.table_query import TableQuery
from iggybase import utilities as util
from .invoice import Invoice
import logging

class InvoiceCollection:
    # either a table_name or a table_query_id must be supplied
    def __init__ (self, year = None, month = None):
        last_month = datetime.datetime.now() + relativedelta(months=-1)
        if not year:
            year = last_month.year
        if not month:
            month = last_month.month
        self.month = month
        self.year = year
        from_date, to_date = self.parse_dates()
        self.oac = g_helper.get_org_access_control()
        self.invoices = self.get_invoices(from_date, to_date)
        self.set_invoices()
        self.populate_tables()
        self.table_query_criteria = {
                ('line_item', 'date_created'): {'from': from_date, 'to': to_date},
                ('line_item', 'price_per_unit'): {'compare': 'greater than',
                    'value': 0}
        }
        self.table_query = TableQuery(None, 1, 'Line Item', 'line_item',
                self.table_query_criteria)

    def parse_dates(self):
        from_date = datetime.date(year=self.year, month=self.month, day=1)
        to_date = from_date + relativedelta(months=1)
        return from_date, to_date

    def get_invoices(self, from_date, to_date):
        invoices = {} # line_items by org_id
        res = self.oac.get_line_items(from_date, to_date)
        item_dict = {}
        for row in res:
            org_id = row.Order.organization_id
            if org_id in item_dict:
                item_dict[org_id].append(row)
            else:
                item_dict[org_id] = [row]
        for org_id, item_list in item_dict.items():
            invoices[org_id] = Invoice(org_id, item_list)
        return invoices

    def set_invoices(self):
        for invoice in self.invoices.values():
            if invoice.total:
                invoice.set_invoice()

    def populate_tables(self):
        for invoice in self.invoices.values():
            invoice.populate_tables()

    def get_select_options(self):
        self.select_years = util.get_last_x_years(5)
        self.select_months = util.get_months_dict()
