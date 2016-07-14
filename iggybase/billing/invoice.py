from flask import request, g
from collections import OrderedDict
from iggybase import utilities as util
from iggybase import g_helper
from .item import Item
import os
import glob
import logging
import time

class Invoice:
    def __init__ (self, from_date, to_date, items, order):
        self.items = self.populate_items(items)
        self.from_date = from_date
        self.to_date = to_date
        self.order = order

        self.org_name = self.items[0].Organization.name
        self.org_id = self.items[0].Organization.id

        # set by set_invoice
        self.id = None
        self.last_modified = None
        self.name = None
        self.Invoice = None

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

        self.core_prefix = {
                'bauer': 'SC',
                'helium': 'HU'
        }
        self.pdf_prefix = (
                self.core_prefix[g.facility]
                + self.get_organization_type_prefix()
                + '-' + str(self.from_date.year) +  '{:02d}'.format(self.from_date.month)
                + '-' + util.zero_pad(self.order, 4)
        )

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
        invoice_row = None
        for item in self.items:
            invoice_row = item.Invoice
            if invoice_row:
                break
        # if new, insert invoice row
        if not invoice_row:
            cols = {
                'invoice_organization_id': self.org_id,
                'amount': int(self.total),
                'order_id': self.items[0].Order.id,
                'invoice_month': self.from_date,
                'order': self.order
            }
            invoice_row = self.oac.insert_row('invoice', cols)

        self.id = invoice_row.id
        self.name = invoice_row.name
        self.last_modified = invoice_row.last_modified
        self.Invoice = invoice_row

        # update line_item if invoice_id not set
        if self.id:
            to_update = []
            for item in self.items:
                if not item.LineItem.invoice_id:
                        to_update.append(item.LineItem)
            if to_update:
                updated = self.oac.update_obj_rows(
                        to_update,
                        {'invoice_id': self.id}
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

    def get_pdf_list(self):
        pdf_list = []
        url = self.get_pdf_dir()
        file_match = url + self.pdf_prefix
        past_pdfs = glob.glob(file_match + '*.pdf')
        for p in past_pdfs:
            pdf_list.append(p.replace(url, ''))
        pdf_list.sort(reverse=True)
        return pdf_list

    def get_next_pdf_name(self):
        url = self.get_pdf_dir()
        file_match = url + self.pdf_prefix
        past_pdfs = glob.glob(file_match + '*.pdf')
        max_ver = 0
        if past_pdfs:
            for p in past_pdfs:
                ver = p.replace((file_match + '-'), '').replace('.pdf', '')
                if ver.isnumeric():
                    ver_int = int(ver)
                    if ver_int > max_ver:
                        max_ver = ver_int
        new_ver = max_ver + 1
        name = self.pdf_prefix + '-' + str(new_ver) + '.pdf'
        return name

    def get_pdf_dir(self):
        return (
                'files/invoice/'
                + self.name.replace(' ', '_').lower()
                + '/'
        )

    def get_pdf_path(self):
        path = self.get_pdf_dir()
        if not os.path.exists(path):
            os.makedirs(path)
        path += self.get_next_pdf_name()
        return path

    def get_pdf_string(self):
        pdf_list = [self.get_next_pdf_name()]
        pdf_list.extend(self.get_pdf_list())
        return '|'.join(pdf_list)

    def update_pdf_name(self):
        self.oac.update_obj_rows([self.Invoice], {'pdf':self.get_pdf_string()})

    def get_organization_type_prefix(self):
        prefix = ''
        if self.items[0].OrganizationType.name == 'harvard':
            prefix = 'ib'
        return prefix

