from flask import g, abort
from iggybase import core, templating
from flask.ext.security import login_required
from . import murray
import iggybase.core.table_query_collection as tqc

@murray.route('/')
def default():
    return templating.page_template('index.html')

@murray.route( '/update_ordered/<table_name>/ajax' )
@login_required
def update_ordered_ajax(facility_name, table_name):
    return core.routes.build_summary_ajax(table_name, 'update', {('status', 'name'):'ordered'})

@murray.route( '/update_ordered/<table_name>/' )
@login_required
def update_ordered(facility_name, table_name):
    # update ordered to received
    page_form = 'update'
    table_queries = tqc.TableQueryCollection(page_form, table_name,
            {('status', 'name'):'ordered'})
    tq = table_queries.get_first()
    hidden_fields = {}
    hidden_fields['column_defaults'] = '{"status":1, "received":"now"}'
    # TODO if we can sort out foreign keys for the update then
    # we don't need to pass in button text
    hidden_fields['button_text'] = 'Receive Selected Oligos'
    hidden_fields['message_fields'] = '["oligo name"]'
    # if nothing to display then page not found
    if not tq.fc.fields:
        abort(403)

    return templating.page_template('update',
            module_name = 'murray',
            table_name = table_name,
            table_query = tq, hidden_fields = hidden_fields)

@murray.route( '/update_requested/<table_name>/ajax' )
@login_required
def update_requested_ajax(facility_name, table_name):
    # TODO: we should really get rid of module name being passed around
    return core.routes.build_summary_ajax(table_name, 'update', {('status', 'name'):'requested'})

@murray.route( '/update_requested/<table_name>/' )
@login_required
def update_requested(facility_name, table_name):
    # update requested to ordered
    page_form = 'update'
    table_queries = tqc.TableQueryCollection(page_form, table_name,
            {('name', 'status'):'requested'})
    tq = table_queries.get_first()
    hidden_fields = {}
    hidden_fields['column_defaults'] = '{"status":2, "ordered":"now"}'
    hidden_fields['button_text'] = 'Order Selected Oligos'
    hidden_fields['message_fields'] = '["oligo name", "sequence"]'
    # if nothing to display then page not found
    if not tq.fc.fields:
        abort(403)

    return templating.page_template('update',
            module_name = 'murray',
            table_name = table_name,
            table_query = tq, hidden_fields = hidden_fields)

@murray.route( '/cancel/<table_name>/ajax' )
@login_required
def cancel_ajax(facility_name, table_name):
    return core.routes.build_summary_ajax(table_name, 'update', {('status', 'name'):['ordered', 'requested']})

@murray.route( '/cancel/<table_name>/' )
@login_required
def cancel(facility_name, table_name):
    # update ordered to received
    page_form = 'update'
    table_queries = tqc.TableQueryCollection(page_form, table_name,
            {('status', 'name'):['ordered', 'requested']})
    tq = table_queries.get_first()
    hidden_fields = {}
    hidden_fields['column_defaults'] = '{"status":3}'
    # TODO if we can sort out foreign keys for the update then
    # we don't need to pass in button text
    hidden_fields['button_text'] = 'Cancel Selected Oligos'
    hidden_fields['message_fields'] = '["oligo name"]'
    # if nothing to display then page not found
    if not tq.fc.fields:
        abort(403)
    return templating.page_template('update',
            module_name = 'murray',
            table_name = table_name,
            table_query = tq, hidden_fields = hidden_fields)
