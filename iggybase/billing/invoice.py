from flask import request, g
from collections import OrderedDict
from iggybase import utilities as util
from iggybase import g_helper
from .item import Item

class Invoice:
    def __init__ (self, org_id, items):
        self.org_id = org_id
        self.items = self.populate_items(items)
        self.Invoice = None # set by set_invoice
        self.oac = g_helper.get_org_access_control()

        # set in total_items
        self.orders = self.group_by('Order', 'id')
        self.users = self.group_by('User', 'id')
        self.total = self.set_total()

        # below are for the template
        self.facility_title = 'Harvard University Sequencing Facility'
        self.from_address = [
                'FAS Division of Science',
                'Northwest Lab Room B227.30',
                '52 Oxford Street',
                'Cambridge, MA 02138'
        ]
        self.purchase_table = []
        self.charges_table = []
        self.user_table = []

    def populate_items(self, items):
        item_list = []
        for item in items:
            item_list.append(Item(item))
        return item_list

    # set total amount
    def set_total(self):
        total = 0
        for item in self.items:
            total += item.amount
        return total

    # group items by order and by users
    def group_by(self, table_name, field_name):
        grouped = OrderedDict()
        for item in self.items:
            table = getattr(item, table_name)
            field_val = getattr(table, field_name)
            if field_val in grouped:
                grouped[field_val]['items'].append(item)
                grouped[field_val]['amount'] += item.amount
            else:
                grouped[field_val] = {
                        'items': [item],
                        'amount': item.amount
                }
        return grouped

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
        self.get_charge_method()
        self.charge_table = self.populate_charges()
        self.user_table = self.populate_users()

    def populate_purchase(self):
        rows = []
        for item in self.items:
            row = OrderedDict()
            if item.amount:
                row['user'] = item.User.name
                row['order'] = item.Order.name
                row['delivery date'] = item.LineItem.date_created
                row['description'] = item.PriceItem.name
                row['amount charged'] =  item.display_amount
                rows.append(row)
        return rows

    def populate_charges(self):
        rows = []
        for order in self.orders.values():
            if order['amount']:
                for data in order['charges']:
                    row = OrderedDict()
                    row['order'] = data['charge'].Order.name
                    row['expense code'] = data['charge'].ChargeMethod.code
                    row['amount charged'] = "${:.2f}".format(data['amount'])
                    row['total charged'] = "${:.2f}".format(data['amount'])
                    rows.append(row)
        return rows

    def get_charge_method(self):
        for order_id, order in self.orders.items():
            self.orders[order_id]['charges'] = []
            charges = self.oac.get_charge_method(order_id)
            amount_remaining = order['amount']
            for charge in charges:
                if amount_remaining:
                    amount_charged = (order['amount'] *
                    (int(charge.OrderChargeMethod.percent or 0)/100))
                    if amount_charged:
                        self.orders[order_id]['charges'].append({
                                'charge': charge,
                                'amount': amount_charged
                        })
                        amount_remaining -= amount_charged

    def populate_users(self):
        rows = []
        for user in self.users.values():
            row = OrderedDict()
            if user['amount']:
                name = user['items'][0].User.name
                row['user'] = name
                row['amount'] = "${:.2f}".format(user['amount'])
                rows.append(row)
        return rows


