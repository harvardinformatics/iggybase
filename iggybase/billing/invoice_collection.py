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
        self.calc_amount()
        self.set_invoices()
        self.populate_tables()

    def parse_dates(self):
        from_date = datetime.date(year=self.year, month=self.month, day=1)
        to_date = from_date + relativedelta(months=1)
        return from_date, to_date

    def get_invoices(self, from_date, to_date):
        invoices = {} # line_items by org_id
        line_items = self.oac.get_line_items(from_date, to_date)
        for item in line_items:
            org_id = item.Order.organization_id
            if org_id in invoices:
                invoices[org_id].add_item(item)
            else:
                invoices[org_id] = Invoice(org_id, [item])
        return invoices

    def calc_amount(self):
        for invoice in self.invoices.values():
            invoice.calc_amount()

    def set_invoices(self):
        for invoice in self.invoices.values():
            if invoice.amount:
                invoice.set_invoice()

    def populate_tables(self):
        for invoice in self.invoices.values():
            invoice.populate_tables()

