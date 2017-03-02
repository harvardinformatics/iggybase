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
    def __init__ (self, from_date, to_date, items, order, service_prefix,
            service_type_id):
        self.items = self.populate_items(items)
        self.from_date = from_date
        self.to_date = to_date
        self.order = order
        self.service_prefix = service_prefix
        self.service_type_id = service_type_id

        self.first_item = next(iter(self.items.values()))
        self.org_name = self.first_item.Organization.name
        self.org_id = self.first_item.Organization.id
        self.charge_method_type = self.first_item.charge_type

        # set by set_invoice
        self.id = None
        self.last_modified = None
        self.name = None
        self.Invoice = None
        self.number = None

        self.oac = g_helper.get_org_access_control()

        # set in total_items
        self.orders = self.group_by('Order', 'id')
        self.get_charge_method()
        self.users = self.group_by('User', 'id')
        self.total = self.set_total()

        # below are for the template
        self.facility_title = 'Harvard University ' + g.rac.facility.banner_title
        self.from_address = [
                'FAS Division of Science',
                'Northwest Lab Room B227.30',
                '52 Oxford Street',
                'Cambridge, MA 02138'
        ]

        self.core_prefix = {
                'bauer': 'SC',
                'helium': 'HU'
        }
        self.pdf_prefix = (
                g.rac.facility.table_suffix.upper()
                + self.service_prefix.upper()
                + 'IG' # iggybase prefix
                + self.get_organization_type_prefix()
                + '-' + str(self.from_date.year)[2:4] +  '{:02d}'.format(self.from_date.month)
                + '-' + util.zero_pad(self.order, 2)
        )

    def populate_items(self, items):
        item_dict = {}
        for item in items:
            if item.LineItem.name in item_dict:
                item_dict[item.LineItem.name].add_charge(item)
            else:
                item_dict[item.LineItem.name] = Item(item)
        return item_dict

    # set total amount
    def set_total(self):
        total = 0
        for item in self.items.values():
            total += item.amount
        return total

    # group items by order and by users
    def group_by(self, table_name, field_name):
        grouped = OrderedDict()
        for item in self.items.values():
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
        for item in self.items.values():
            invoice_row = item.Invoice
            if invoice_row:
                break
        # if new, insert invoice row
        if not invoice_row:
            cols = {
                'invoice_organization_id': self.org_id,
                'amount': int(self.total),
                'order_id': self.first_item.Order.id,
                'invoice_month': self.from_date,
                'order': self.order,
                'service_type_id': self.service_type_id,
                'active': 1,
                'invoice_number': self.order
            }
            invoice_row = self.oac.insert_row('invoice', cols)
        self.id = invoice_row.id
        self.name = invoice_row.name
        self.last_modified = invoice_row.last_modified
        self.Invoice = invoice_row
        self.number = self.get_next_name()
        # update line_item with invoice_id
        if self.id:
            to_update = []
            for item in self.items.values():
                to_update.append(item.LineItem)
            if to_update:
                updated = self.oac.update_obj_rows(
                        to_update,
                        {'invoice_id': self.id}
                )
                if not updated:
                    logging.error('Invoice_id not updated to ' + str(invoice_id)
                            + ' for line_items: ' + json.dumps(to_update))


    def populate_template_data(self):
        self.purchase_table = self.populate_purchase()
        self.contacts = self.get_contact_info()
        self.to_info = self.populate_to_info()
        if self.charge_method_type == 'po':
            self.po_info = self.populate_po_info()
        else:
            self.charge_table = self.populate_charges()
            self.user_table = self.populate_users()

    def populate_purchase(self):
        rows = []
        for item in self.items.values():
            row = OrderedDict()
            if item.amount:
                row['user'] = item.User.name
                row['order'] = item.Order.name
                row['delivery date'] = item.LineItem.date_created.date()
                row['description'] = item.PriceItem.name
                row['quantity'] = item.LineItem.quantity
                row['price per unit'] = item.LineItem.price_per_unit
                row['amount'] =  item.display_amount
                rows.append(row)
        return rows

    def get_contact_by_position(self, org_id, position):
        users = self.oac.get_org_position(self.org_id, position)
        contacts = []
        for u in users:
            if u.first_name and u.last_name:
                name = u.first_name + ' ' + u.last_name
            else:
                name = u.name
            contacts.append({'name':name, 'email':u.email})
        return contacts

    def get_contact_info(self):
        manager = self.get_contact_by_position(self.org_id, 'manager')
        pi = self.get_contact_by_position(self.org_id, 'pi')
        return {'manager': manager, 'pi': pi}

    def get_contacts_as_list(self, position, attr):
        attrs = []
        if position in self.contacts:
            for contact in self.contacts[position]:
                if attr in contact:
                    attrs.append(contact[attr])
        return ', '.join(attrs)

    def populate_to_info(self):
        if self.charge_method_type == 'po':
            info = OrderedDict()
            info['PI'] = self.get_contacts_as_list('pi', 'name')
            info['Institution'] = getattr(self.first_item.Institution, 'name', '')
            info['PO Number'] = self.first_item.ChargeMethod.code
        else:
            mng_names = self.get_contacts_as_list('manager', 'name')
            mng_emails = self.get_contacts_as_list('manager', 'email')
            info = OrderedDict()
            info['Sent to'] =  mng_names
            info['Email'] = mng_emails
        return info

    def populate_po_info(self):
        if self.first_item.ChargeMethod.billing_address:
            address = self.fist_item.ChargeMethod.billing_address.split(",")
        else:
            address = []

        info = {
                'invoice address': address,
                'remit to': [
                    [
                        'Harvard University',
                        'Accounts Receivable',
                        'PO Box 4999',
                        'Boston, MA 02212-4999',
                        'ar_customers@harvard.edu',
                        '617-495-3787'
                    ],
                    [
                        'Please inlude Invoice number on remittance',
                        'Harvard Tax ID No: 05-2103580'
                        'Harvard DUNS 082359691',
                        'Bank transfer fees are the responsibility of the payer'
                    ]
                ]
        }
        return info

    def populate_charges(self):
        rows = []
        for order in self.orders.values():
            if order['amount']:
                for data in order['charges']:
                    row = OrderedDict()
                    row['order'] = data['charge'].Order.name
                    row['expense code'] = data['charge'].ChargeMethod.code
                    row['percent charged'] = int(data['charge'].OrderChargeMethod.percent or 0)
                    row['amount charged'] = "${:.2f}".format(data['amount'])
                    row['amount credited'] = "${:.2f}".format(0)
                    row['total charged'] = "${:.2f}".format(data['amount'])
                    rows.append(row)
        return rows

    def get_charge_method(self):
        charges = {}
        for order_id, order in self.orders.items():
            self.orders[order_id]['charges'] = []
            amount_remaining = order['amount']
            for item in order['items']:
                charges.update(item.charges)
            for charge in charges.values():
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
        return self.get_next_name() + '.pdf'

    def get_next_name(self):
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
        name = self.pdf_prefix + '-' + str(new_ver)
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
        if self.first_item.OrganizationType.name == 'harvard':
            prefix = 'ib'
        return prefix

