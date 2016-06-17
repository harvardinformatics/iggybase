from flask import request, g
from collections import OrderedDict
from iggybase import utilities as util
from iggybase import g_helper

class Invoice:
    def __init__ (self, org_id, items):
        self.org_id = org_id
        self.items = items
        self.Invoice = None # set by set_invoice
        self.oac = g_helper.get_org_access_control()
        self.line_amounts = {}

        # below are for the template
        self.facility_title = 'Harvard University Sequencing Facility'
        self.from_address = [
                'FAS Division of Science',
                'Northwest Lab Room B227.30',
                '52 Oxford Street',
                'Cambridge, MA 02138'
        ]
        self.purchase_table = []

    def add_item(self, item):
        self.items.append(item)

    def calc_amount(self):
        amount = 0
        for item in self.items:
            line_amount = (int(item.LineItem.price_per_unit or 0) * int(item.LineItem.quantity or 1))
            self.line_amounts[item.LineItem.name] = line_amount
            amount += line_amount
        self.amount = amount

    def set_invoice(self):
        # find invoice id
        invoice_id = None
        for item in self.items:
            invoice_id = item.LineItem.invoice_id
            if invoice_id:
                break

        # fetch or insert invoice row
        if invoice_id:
            self.Invoice = self.oac.get_row('invoice', {'id': invoice_id})
        else:
            cols = {
                'invoice_organization_id': self.org_id,
                'amount': int(self.amount),
                'order_id': self.items[0].Order.id
            }
            self.Invoice = self.oac.insert_row('invoice', cols)

        # update line_item if invoice_id not set
        if self.Invoice:
            for item in self.items:
                if not item.LineItem.invoice_id:
                        self.oac.update_rows(
                                'line_item',
                                {'invoice_id': self.Invoice.id},
                                [item.LineItem.id]
                        )

    def populate_tables(self):
        self.purchase_table = self.populate_purchase()

    def populate_purchase(self):
        rows = []
        for item in self.items:
            line_amount = self.line_amounts[item.LineItem.name]
            if line_amount:
                row = OrderedDict()
                row['requester'] = item.User.name
                row['delivery date'] = item.LineItem.date_created
                row['description'] = item.PriceItem.name
                row['amount charged'] =  self.line_amounts[item.LineItem.name]
                rows.append(row)
        return rows

