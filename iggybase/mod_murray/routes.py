from flask import g, abort
from iggybase import mod_core, templating
from flask.ext.security import login_required, current_user
from iggybase.mod_murray import mod_murray
import iggybase.table_query_collection as tqc

@mod_murray.before_request
@login_required
def before_request():
    g.user = current_user

@mod_murray.route('/')
def default():
    return templating.page_template('index.html')

@mod_murray.route( '/update_ordered/<table_name>/ajax' )
@login_required
def update_ordered_ajax(facility_name, table_name):
    return mod_core.routes.summary_ajax(facility_name, 'murray', table_name, 'update', {('status', 'name'):'ordered'})

@mod_murray.route( '/update_ordered/<table_name>/' )
@login_required
def update_ordered(facility_name, table_name):
    # update ordered to received
    page_form = 'update'
    table_queries = tqc.TableQueryCollection(facility_name, 'murray', page_form, table_name,
            {('status', 'name'):'ordered'})
    table_queries.get_fields()
    first_table_query = table_queries.get_first()
    hidden_fields = {}
    hidden_fields['column_defaults'] = '{"status":1, "received":"now"}'
    # TODO if we can sort out foreign keys for the update then
    # we don't need to pass in button text
    hidden_fields['button_text'] = 'Receive Selected Oligos'
    hidden_fields['message_fields'] = '["name"]'
    # if nothing to display then page not found
    if not first_table_query.table_fields:
        abort(403)

    return templating.page_template('update',
            module_name = 'murray',
            table_name = table_name,
            table_query = first_table_query, hidden_fields = hidden_fields)

@mod_murray.route( '/update_requested/<table_name>/ajax' )
@login_required
def update_requested_ajax(facility_name, table_name):
    # TODO: we should really get rid of module name being passed around
    return mod_core.routes.summary_ajax(facility_name, 'murray', table_name, 'update', {('status', 'name'):'requested'})

@mod_murray.route( '/update_requested/<table_name>/' )
@login_required
def update_requested(facility_name, table_name):
    # update requested to ordered
    page_form = 'update'
    table_queries = tqc.TableQueryCollection(facility_name, 'murray', page_form, table_name,
            {('name', 'status'):'requested'})
    table_queries.get_fields()
    first_table_query = table_queries.get_first()
    hidden_fields = {}
    hidden_fields['column_defaults'] = '{"status":2, "ordered":"now"}'
    hidden_fields['button_text'] = 'Order Selected Oligos'
    hidden_fields['message_fields'] = '["name", "sequence"]'
    # if nothing to display then page not found
    if not first_table_query or not first_table_query.table_fields:
        abort(403)

    return templating.page_template('update',
            module_name = 'murray',
            table_name = table_name,
            table_query = first_table_query, hidden_fields = hidden_fields)

@mod_murray.route( '/cancel/<table_name>/ajax' )
@login_required
def cancel_ajax(facility_name, table_name):
    return mod_core.routes.summary_ajax(facility_name, 'murray', table_name, 'update', {('status', 'name'):['ordered', 'requested']})

@mod_murray.route( '/cancel/<table_name>/' )
@login_required
def cancel(facility_name, table_name):
    # update ordered to received
    page_form = 'update'
    table_queries = tqc.TableQueryCollection(facility_name, 'murray', page_form, table_name,
            {('status', 'name'):['ordered', 'requested']})
    table_queries.get_fields()
    first_table_query = table_queries.get_first()
    hidden_fields = {}
    hidden_fields['column_defaults'] = '{"status":3}'
    # TODO if we can sort out foreign keys for the update then
    # we don't need to pass in button text
    hidden_fields['button_text'] = 'Cancel Selected Oligos'
    hidden_fields['message_fields'] = '["name"]'
    # if nothing to display then page not found
    if not first_table_query.table_fields:
        abort(403)
    return templating.page_template('update',
            module_name = 'murray',
            table_name = table_name,
            table_query = first_table_query, hidden_fields = hidden_fields)
