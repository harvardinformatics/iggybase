from flask import render_template
from flask.ext.security import login_required
from . import billing
from iggybase import core, templating
from iggybase.billing.invoice_collection import InvoiceCollection
from iggybase.decorators import templated

@billing.route('/')
@templated()
def default():
    return templating.page_template_context('index.html')

@billing.route('/invoice/<year>/<month>', defaults={'page_context': 'base-context'})
@billing.route( '/invoice/<year>/<month>/<page_context>' )
@login_required
def invoice(facility_name, year, month, page_context):
    template = 'invoice_generator'
    print('invoice gen')
    ic = InvoiceCollection(int(year), int(month))
    return render_template('invoice_base.html',
            module_name = 'billing',
            invoice = ic.invoices[84])

