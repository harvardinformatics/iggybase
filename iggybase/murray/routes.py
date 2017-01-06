from flask import abort
from flask.ext.security import login_required
from iggybase.web_files.decorators import templated
import json
import iggybase.core.table_query_collection as tqc
from iggybase import core
from iggybase.web_files.page_template import PageTemplate
from . import murray


@murray.route('/')
@templated()
def default():
    pt = PageTemplate('murray', 'index')
    return pt.page_template_context()


@murray.route( '/update_ordered/<table_name>/ajax' )
@login_required
def update_ordered_ajax(facility_name, table_name):
    return core.routes.build_summary_ajax(table_name, {('oligo', 'status'):'ordered'})


@murray.route( '/update_ordered/<table_name>/' )
@login_required
@templated()
def update_ordered(facility_name, table_name):
    # update ordered to received
    table_queries = tqc.TableQueryCollection(table_name,
            {('oligo', 'status'):'ordered'})
    tq = table_queries.get_first()
    hidden_fields = {}
    oligo_status_received = table_queries.oac.get_select_list_item('oligo', 'status', 'Received')
    hidden_fields['column_defaults'] = json.dumps({"oligo":{"status":oligo_status_received.id, "received":"now"}})
    # TODO if we can sort out foreign keys for the update then
    # we don't need to pass in button text
    hidden_fields['button_text'] = 'Receive Selected Oligos'
    hidden_fields['message_fields'] = json.dumps(["oligo|oligo_name"])
    # if nothing to display then page not found
    if not tq.fc.fields:
        abort(403)

    pt = PageTemplate('murray', 'update')
    return pt.page_template_context(table_name = table_name, table_query = tq, hidden_fields = hidden_fields)


@murray.route( '/update_requested/<table_name>/ajax' )
@login_required
def update_requested_ajax(facility_name, table_name):
    # TODO: we should really get rid of module name being passed around
    return core.routes.build_summary_ajax(table_name, {('oligo', 'status'):'requested'})


@murray.route( '/update_requested/<table_name>/' )
@login_required
@templated()
def update_requested(facility_name, table_name):
    # update requested to ordered
    table_queries = tqc.TableQueryCollection(table_name,
            {('oligo', 'status'):'requested'})
    tq = table_queries.get_first()
    hidden_fields = {}
    oligo_status_ordered = table_queries.oac.get_select_list_item('oligo', 'status', 'Ordered')
    hidden_fields['column_defaults'] = json.dumps({"oligo":{"status":oligo_status_ordered.id, "ordered":"now"}})
    hidden_fields['button_text'] = 'Order Selected Oligos'
    hidden_fields['message_fields'] = json.dumps(["oligo|oligo_name", "oligo|sequence"])
    # if nothing to display then page not found
    if not tq.fc.fields:
        abort(403)

    pt = PageTemplate('murray', 'update')
    return pt.page_template_context(table_name = table_name, table_query = tq, hidden_fields = hidden_fields)


@murray.route( '/cancel/<table_name>/ajax' )
@login_required
def cancel_ajax(facility_name, table_name):
    return core.routes.build_summary_ajax(table_name, {('oligo', 'status'):['ordered', 'requested']})


@murray.route( '/cancel/<table_name>/' )
@login_required
@templated()
def cancel(facility_name, table_name):
    # update ordered to received
    table_queries = tqc.TableQueryCollection(table_name,
            {('oligo', 'status'):['ordered', 'requested']})
    tq = table_queries.get_first()
    hidden_fields = {}
    oligo_status_canceled = table_queries.get_select_list_item('oligo', 'status', 'Canceled')
    hidden_fields['column_defaults'] = json.dumps({"oligo":{"status":oligo_status_canceled.id}})
    # TODO if we can sort out foreign keys for the update then
    # we don't need to pass in button text
    hidden_fields['button_text'] = 'Cancel Selected Oligos'
    hidden_fields['message_fields'] = json.dumps(["oligo|oligo_name"])
    # if nothing to display then page not found
    if not tq.fc.fields:
        abort(403)

    pt = PageTemplate('murray', 'update')
    return pt.page_template_context(table_name = table_name, table_query = tq, hidden_fields = hidden_fields)
