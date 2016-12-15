import json
from flask import render_template, request, flash
from flask.ext.security import login_required
from flask_weasyprint import render_pdf, HTML
from iggybase.web_files.decorators import templated
from iggybase import utilities as util
from iggybase import g_helper
from iggybase.web_files.page_template import PageTemplate
from iggybase.core import routes as core_routes
from iggybase.core.table_query_collection import TableQueryCollection
from iggybase.billing.invoice_collection import InvoiceCollection
from iggybase.billing.line_item_collection import LineItemCollection
from . import billing

MODULE_NAME = 'billing'


@billing.route( '/review/' )
@billing.route( '/review/<int:year>/<int:month>/' )
@login_required
@templated()
def review(facility_name, year = None, month = None):
    # options for dropdowns
    select_years = util.get_last_x_years(5)
    select_months = util.get_months_dict()

    if not month or not year: #mostly we default to last_month
        # default to last month, get start and end dates
        last_month = util.get_last_month()
        year = last_month.year
        month = last_month.month

    from_date, to_date = util.start_and_end_month(year, month)

    # get line_items for month
    criteria = {
            ('line_item', 'date_created'): {'from': from_date, 'to': to_date},
            ('line_item', 'price_per_unit'): {'compare': 'greater than', 'value': 0}
    }
    tqc = TableQueryCollection('line_item', criteria)
    table_query = tqc.get_first()
    pt = PageTemplate(MODULE_NAME, 'review')
    return pt.page_template_context(
            year = year, month = month,
            select_years = select_years, select_months = select_months,
            table_name = 'line_item', table_query = table_query
    )


@billing.route( '/review/<int:year>/<int:month>/ajax/' )
@login_required
def review_ajax(facility_name, year, month):
    from_date, to_date = util.start_and_end_month(year, month)
    criteria = {
            ('line_item', 'date_created'): {'from': from_date, 'to': to_date},
            ('line_item', 'price_per_unit'): {'compare': 'greater than', 'value': 0}
    }
    return core_routes.build_summary_ajax('line_item', criteria)




@billing.route( '/invoice_summary/<int:year>/<int:month>/' )
@login_required
@templated()
def invoice_summary(facility_name, year, month):
    # options for dropdowns
    select_years = util.get_last_x_years(5)
    select_months = util.get_months_dict()
    from_date, to_date = util.start_and_end_month(year, month)

    criteria = {
            ('invoice', 'invoice_month'): {'from': from_date, 'to': to_date},
    }
    tqc = TableQueryCollection('invoice', criteria)
    hidden_fields = {'year': year, 'month': month}
    pt = PageTemplate(MODULE_NAME, 'invoice_summary')
    return pt.page_template_context(
            select_years = select_years, select_months = select_months,
            year = year, month = month, from_date = from_date, table_name = 'invoice', table_query = tqc.queries[0],
            hidden_fields = hidden_fields, facility_name = facility_name
    )


@billing.route( '/invoice_summary/<int:year>/<int:month>/ajax/' )
@login_required
def invoice_summary_ajax(facility_name, year, month):
    from_date, to_date = util.start_and_end_month(year, month)
    criteria = {
            ('invoice', 'invoice_month'): {'from': from_date, 'to': to_date},
    }
    return core_routes.build_summary_ajax('invoice', criteria)


@billing.route('/generate_invoices/<int:year>/<int:month>/', methods=['GET', 'POST'])
@login_required
def generate_invoices(facility_name, year, month):
    orgs = []
    if request.data:
        post_params = request.get_json()
        if 'orgs' in post_params:
            orgs = post_params['orgs']
    ic = InvoiceCollection(year, month, orgs) # defaults to last complete
    ic.populate_template_data()
    # can't update the pdf name in db after generation because pdf generation
    # borks the db_session for the request
    ic.update_pdf_names()
    generated = ic.generate_pdfs()
    if generated:
        flash('Successfully generated: ' + ', '.join(generated))
    return json.dumps({'generated':generated})


@billing.route( '/invoice/<int:year>/<int:month>/' )
@billing.route( '/invoice/<int:year>/<int:month>/<org_name>/' )
@login_required
def invoice(facility_name, year, month, org_name = None):
    org_list = []
    if org_name:
        org_list.append(org_name)
    ic = InvoiceCollection(year, month, org_list)
    ic.populate_template_data()
    return render_template('invoice_base.html',
            module_name = 'billing',
            invoices=ic.invoices)


@billing.route( '/invoice/invoice-<int:year>-<int:month>.pdf' )
@billing.route( '/invoice/invoice-<int:year>-<int:month>-<org_name>.pdf' )
@login_required
def invoice_pdf(facility_name, year, month, org_name = None):
    html = (invoice(facility_name = facility_name,
            year = year, month = month, org_name = org_name))
    return render_pdf(HTML(string=html))

@billing.route('/get_price/ajax', methods=['GET', 'POST'])
@login_required
def get_price(facility_name):
    criteria = request.json['criteria']
    fields = request.json['fields']
    oac = g_helper.get_org_access_control()
    row = oac.get_price(criteria)
    price = None
    ret = {}
    if row:
        for field in fields:
            ret[field] = str(getattr(row, field))
    return json.dumps(ret)

@billing.route( '/reports/' )
@billing.route( '/reports/<int:year>/<int:month>/' )
@login_required
@templated()
def reports(facility_name, year = None, month = None):
    # options for dropdowns
    select_years = util.get_last_x_years(5)
    select_months = util.get_months_dict()

    if not month or not year: #mostly we default to last_month
        # default to last month, get start and end dates
        last_month = util.get_last_month()
        year = last_month.year
        month = last_month.month

    lc = LineItemCollection(year, month)
    lc.populate_report_data()
    pt = PageTemplate(MODULE_NAME, 'reports')
    return pt.page_template_context(
            lc = lc, year = year, month = month,
            select_years = select_years, select_months = select_months)



