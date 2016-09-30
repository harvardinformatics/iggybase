import json

from flask import render_template, request
from flask.ext.security import login_required
from flask_weasyprint import render_pdf, HTML
from iggybase.web_files.decorators import templated

from iggybase.web_files.page_template import PageTemplate
from iggybase import core
from iggybase.billing.invoice_collection import InvoiceCollection
from . import billing

MODULE_NAME = 'billing'


@billing.route( '/review/' )
@login_required
@templated()
def review(facility_name):
    ic = InvoiceCollection() # defaults to last complete
    ic.get_select_options()
    ic.get_table_query_collection('line_item')
    table_query = ic.tqc.get_first()

    pt = PageTemplate(MODULE_NAME, 'review')
    return pt.page_template_context(ic = ic, table_name = 'line_item', table_query = table_query)


@billing.route( '/review/<year>/<month>/ajax/' )
@login_required
def review_ajax(facility_name, year, month):
    ic = InvoiceCollection(int(year), int(month)) # year and month set in js
    return core.routes.build_summary_ajax('line_item', ic.table_query_criteria['line_item'])




@billing.route( '/invoice_summary/<year>/<month>/' )
@login_required
@templated()
def invoice_summary(facility_name, year, month):
    ic = InvoiceCollection(int(year), int(month)) # defaults to last complete
    ic.get_select_options()
    ic.get_table_query_collection('invoice')
    hidden_fields = {'year': year, 'month': month}

    pt = PageTemplate(MODULE_NAME, 'invoice_summary')
    return pt.page_template_context(ic = ic, table_name = 'invoice', table_query = ic.tqc.queries[0],
                                    hidden_fields = hidden_fields)


@billing.route( '/invoice_summary/<year>/<month>/ajax/' )
@login_required
def invoice_summary_ajax(facility_name, year, month):
    ic = InvoiceCollection(int(year), int(month)) # defaults to last complete
    return core.routes.build_summary_ajax('invoice', ic.table_query_criteria['invoice'])




@billing.route('/generate_invoices/<year>/<month>/', methods=['GET', 'POST'])
@login_required
def generate_invoices(facility_name, year, month):
    orgs = []
    if request.data:
        post_params = request.get_json()
        if 'orgs' in post_params:
            orgs = post_params['orgs']
    ic = InvoiceCollection(int(year), int(month), orgs) # defaults to last complete
    ic.populate_template_data()
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
    ic.populate_template_data()
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
