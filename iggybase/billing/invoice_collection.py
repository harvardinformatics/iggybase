from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta
from iggybase import g_helper
from .invoice import Invoice
import logging

class InvoiceCollection:
    # either a table_name or a table_query_id must be supplied
    def __init__ (self, year, month):
        self.month = month
        self.year = year
        from_date, to_date = self.parse_dates()
        self.oac = g_helper.get_org_access_control()
        self.invoices = self.get_invoices(from_date, to_date)
        self.total_items()
        self.set_invoices()
        self.populate_tables()

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

    def total_items(self):
        for invoice in self.invoices.values():
            invoice.total_items()

    def set_invoices(self):
        for invoice in self.invoices.values():
            if invoice.total:
                invoice.set_invoice()

    def populate_tables(self):
        for invoice in self.invoices.values():
            invoice.populate_tables()

