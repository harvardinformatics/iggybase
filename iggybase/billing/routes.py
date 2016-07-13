from flask import render_template, request
import json
from collections import OrderedDict
from flask.ext.security import login_required
from . import billing
from iggybase import core, templating
from iggybase.billing.invoice_collection import InvoiceCollection
from iggybase.decorators import templated
import iggybase.templating as templating
from flask_weasyprint import render_pdf, HTML

MODULE_NAME = 'billing'

@billing.route( '/review/' )
@login_required
@templated()
def review(facility_name):
    ic = InvoiceCollection() # defaults to last complete
    ic.get_select_options()
    ic.get_table_query('line_item')
    return templating.page_template_context('review', ic = ic,
        table_name = 'line_item', table_query = ic.table_query,
        module_name=MODULE_NAME)

@billing.route( '/review/<year>/<month>/ajax/' )
@login_required
def review_ajax(facility_name, year, month):
    ic = InvoiceCollection(int(year), int(month)) # year and month set in js
    return core.routes.build_summary_ajax('line_item', 'review',
            ic.table_query_criteria['line_item'])

@billing.route( '/invoice_summary/<year>/<month>/' )
@login_required
@templated()
def invoice_summary(facility_name, year, month):
    ic = InvoiceCollection(int(year), int(month)) # defaults to last complete
    ic.get_select_options()
    ic.get_table_query('invoice')
    hidden_fields = {'year': year, 'month': month}
    return templating.page_template_context('invoice_summary', ic = ic,
            module_name = MODULE_NAME, table_name = 'invoice',
            table_query = ic.table_query, hidden_fields = hidden_fields)

@billing.route( '/invoice_summary/<year>/<month>/ajax/' )
@login_required
def invoice_summary_ajax(facility_name, year, month):
    ic = InvoiceCollection(int(year), int(month)) # defaults to last complete
    return core.routes.build_summary_ajax('invoice', 'invoice_summary',
            ic.table_query_criteria['invoice'])

@billing.route('/generate_invoices/<year>/<month>/', methods=['GET', 'POST'])
@login_required
def generate_invoices(facility_name, year, month):
    orgs = []
    if request.data:
        post_params = request.get_json()
        if 'orgs' in post_params:
            orgs = post_params['orgs']
    ic = InvoiceCollection(int(year), int(month), orgs) # defaults to last complete
    # can't update the pdf name in db after generation because pdf generation
    # borks the db_session for the request
    ic.update_pdf_names()
    generated = ic.generate_pdfs()
    return json.dumps({'generated':generated})


@billing.route( '/invoice/<year>/<month>/' )
@billing.route( '/invoice/<year>/<month>/<org_name>/' )
@login_required
def invoice(facility_name, year, month, org_name = None):
    org_list = []
    if org_name:
        org_list.append(org_name)
    ic = InvoiceCollection(int(year), int(month), org_list)
    return render_template('invoice_base.html',
            module_name = 'billing',
            invoices=ic.invoices)

@billing.route( '/invoice/invoice-<year>-<month>.pdf' )
@billing.route( '/invoice/invoice-<year>-<month>-<org_name>.pdf' )
@login_required
def invoice_pdf(facility_name, year, month, org_name = None):
    html = (invoice(facility_name = facility_name,
            year = year, month = month, org_name = org_name))
    return render_pdf(HTML(string=html))
