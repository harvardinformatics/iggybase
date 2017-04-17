from flask import request, g
from collections import OrderedDict
from iggybase import utilities as util
from iggybase import g_helper
from .item import Item
import datetime as dt
from dateutil.relativedelta import relativedelta
import re
import os
import glob
import logging

class Invoice:
    def __init__ (self, from_date, to_date, items, order, service_prefix,
            service_type_id):
        self.items = self.populate_items(items)
        self.from_date = from_date
        # we will search where less than to_date, so we need to subtract a day
        # to display last day in our range
        self.to_date = to_date - relativedelta(days=1)
        self.order = order
        self.service_prefix = service_prefix
        self.service_type_id = service_type_id

        self.first_item = next(iter(self.items.values()))
        self.first_charge = next(iter(self.first_item.charges.values()))
        self.org_name = self.first_item.Organization.name
        self.org_id = self.first_item.Organization.id
        self.charge_method_type = self.first_item.charge_type

        # set by set_invoice
        self.id = None
        self.last_modified = dt.datetime.today().date()
        self.name = None
        self.Invoice = None
        self.number = None

        self.oac = g_helper.get_org_access_control()

        # set in total_items
        self.orders = self.group_by('Order', 'id')
        self.get_charge_method()
        self.users = self.group_by('User', 'id')
        self.total = self.set_total()
        self.display_total = "${:.2f}".format(self.total)

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
                # service should not get displayed in invoice name
                + (self.service_prefix.upper() if (self.service_prefix != 'service') else '')
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

    def set_invoice(self, single_group):
        # find invoice id
        invoice_row = None
        for item in self.items.values():
            invoice_row = item.Invoice
            if invoice_row:
                break
        # if new, insert invoice row, if not single group
        # invoice number must be assigned in context of the whole month
        if not invoice_row and not single_group:
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
            # if this is a PO then update remaining_value
            if self.charge_method_type == 'po':
                new_amt = (float(self.first_item.ChargeMethod.remaining_value) -
                self.total)
                # TODO: email sunia if less than 0
                updated = self.oac.update_obj_rows(
                        [self.first_item.ChargeMethod],
                        {'remaining_value': new_amt}
                )
        if invoice_row:
            self.id = invoice_row.id
            self.name = invoice_row.name
            self.last_modified = invoice_row.last_modified.date()
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
        # sort items by delivery date
        lst = sorted(list(self.items.values()), key=lambda x: (x.Order.name, x.LineItem.date_created))
        for item in lst:
            row = OrderedDict()
            if item.amount:
                row['user'] = item.User.name
                row['order'] = item.Order.name
                row['delivery date'] = item.LineItem.date_created.date()
                row['description'] = item.PriceItem.name
                row['price per unit'] = "${:.2f}".format(item.LineItem.price_per_unit)
                row['quantity'] = item.LineItem.quantity
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
            info['PO Number'] = self.first_charge.ChargeMethod.code
        else:
            mng_names = self.get_contacts_as_list('manager', 'name')
            mng_emails = self.get_contacts_as_list('manager', 'email')
            info = OrderedDict()
            info['Sent to'] =  mng_names
            info['Email'] = mng_emails
        return info

    def populate_po_info(self):
        address = []
        # custom charge_method address will take precedence
        # TODO: eventually have user enter new address and save id
        if self.first_charge.ChargeMethod.billing_address:
            address = self.first_charge.ChargeMethod.billing_address.split(",")
        # default to the billing address from org
        # TODO: need to display this to user in data entry
        elif self.first_charge.Address.address_1:
            row = self.first_charge.Address
            if row.address_1:
                address.append(row.address_1)
            if row.address_2:
                address.append(row.address_2)
            if row.address_3:
                address.append(row.address_3)
            if row.city or row.state:
                cit_st = [row.city, row.state]
                address.append(', '.join(cit_st))
            if row.postcode:
                address.append(row.postcode)

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
        rows = {}
        for order in self.orders.values():
            if order['amount']:
                for data in order['charges']:
                    clean_code = re.sub("[^0-9]", "", data['charge'].ChargeMethod.code)
                    if clean_code in rows:
                        rows[clean_code]['amount charged'] += data['amount']
                        # current core does not have credits
                        rows[clean_code]['amount credited'] += 0.0
                    else:
                        row = OrderedDict()
                        row['expense code'] = data['charge'].ChargeMethod.code
                        row['amount charged'] = data['amount']
                        row['amount credited'] = 0.0
                        rows[clean_code] = row
        # format the total
        for code, r in rows.items():
            rows[code]['total charged'] = "${:.2f}".format((r['amount charged'] - r['amount credited']))
            rows[code]['amount charged'] = "${:.2f}".format(r['amount charged'])
            rows[code]['amount credited'] = "${:.2f}".format(r['amount credited'])
        # sort by expense code
        lst = sorted(list(rows.values()), key = lambda x: x['expense code'])
        return lst

    def get_charge_method(self):
        for order_id, order in self.orders.items():
            charges = {}
            self.orders[order_id]['charges'] = []
            amount_remaining = order['amount']
            for item in order['items']:
                # each item has all charges for that orde
                # do take them from the first item
                charges = item.charges
                break
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
        # sort by user name
        lst = sorted(list(self.users.values()), key=lambda x: x['items'][0].User.name)
        for user in lst:
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
        if getattr(self.first_item, 'OrganizationType', None) and self.first_item.OrganizationType.name == 'harvard':
            prefix = 'ib'
        return prefix

