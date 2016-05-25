from iggybase import core, templating
from flask.ext.security import login_required
from . import billing
from iggybase.decorators import templated

@billing.route('/')
@templated()
def default():
    return templating.page_template_context('index.html')

@billing.route('/invoice_generator/<table_name>/<row_names>', defaults={'page_context': 'base-context'})
@billing.route( '/invoice_generator/<table_name>/<row_names>/<page_context>' )
@login_required
@templated()
def invoice_generator(facility_name, table_name, row_names, page_context):
    template = 'invoice_generator'
    print('invoice gen')
    return templating.page_template_context(template,
            module_name = 'billing',
            table_name = table_name)

