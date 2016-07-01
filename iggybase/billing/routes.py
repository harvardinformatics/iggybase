from flask import render_template
from collections import OrderedDict
from flask.ext.security import login_required
from . import billing
from iggybase import core, templating
from iggybase.billing.invoice_collection import InvoiceCollection
from iggybase.decorators import templated
import iggybase.templating as templating
from flask_weasyprint import render_pdf, HTML

@billing.route('/')
@templated()
def default():
    return templating.page_template_context('index.html')

@billing.route( '/invoice_summary/' )
@login_required
@templated()
def invoice_summary(facility_name):
    ic = InvoiceCollection(2016, 5) # defaults to last complete
    ic.get_select_options()
    return templating.page_template_context('invoice_summary', ic = ic,
            table_name = 'line_item', table_query = ic.table_query)

@billing.route( '/invoice_summary/ajax/' )
@login_required
def invoice_summary_ajax(facility_name):
    ic = InvoiceCollection(2016, 5) # defaults to last complete
    return core.routes.build_summary_ajax('line_item', 'invoice_summary',
            ic.table_query_criteria)

@billing.route( '/invoice/<year>/<month>/' )
@login_required
def invoice(facility_name, year, month):
    template = 'invoice_generator'
    print('invoice gen')
    ic = InvoiceCollection(int(year), int(month))
    return render_template('invoice_base.html',
            module_name = 'billing',
            invoice = ic.invoices[84])

@billing.route( '/invoice/<year>/<month>/download/' )
@login_required
def invoice_download(facility_name, year, month):
    template = 'invoice_generator'
    print('invoice gen')
    ic = InvoiceCollection(int(year), int(month))
    html = render_template('invoice_base.html',
            module_name = 'billing',
            invoice = ic.invoices[84])
    return render_pdf(HTML(string=html))

