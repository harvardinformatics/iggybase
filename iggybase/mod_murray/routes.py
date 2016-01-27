from flask import g
from iggybase import base_routes, templating
from flask.ext.security import login_required, current_user
from iggybase.mod_murray import mod_murray
import iggybase.table_query_collection as tqc

@mod_murray.before_request
@login_required
def before_request():
    g.user = current_user

@mod_murray.route('/')
def default():
    return templateing.page_template('index.html')

@mod_murray.route( '/update_ordered/<table_name>/ajax' )
@login_required
def update_ordered_ajax(table_name):
    return base_routes.summary_ajax('murray', table_name, {('status', 'name'):'ordered'})

@mod_murray.route( '/update_ordered/<table_name>/' )
@login_required
def update_ordered(table_name):
    # update ordered to received
    page_form = 'summary'
    table_queries = tqc.TableQueryCollection('murray', page_form, table_name,
            {('status', 'name'):'ordered'})
    table_queries.get_fields()
    first_table_query = table_queries.get_first()
    hidden_fields = {}
    hidden_fields['column_defaults'] = '{"status":1}'
    # TODO if we can sort out foreign keys for the update then
    # we don't need to pass in button text
    hidden_fields['button_text'] = 'Receive Selected Oligos'
    # if nothing to display then page not found
    if not first_table_query.table_fields:
        abort(404)
    return templating.page_template('update',
            module_name = 'murray',
            table_name = table_name,
            table_query = first_table_query, hidden_fields = hidden_fields)

@mod_murray.route( '/update_requested/<table_name>/ajax' )
@login_required
def update_requested_ajax(table_name):
    # TODO: we should really get rid of module name being passed around
    return base_routes.summary_ajax('murray', table_name, {('status', 'name'):'requested'})

@mod_murray.route( '/update_requested/<table_name>/' )
@login_required
def update_requested(table_name):
    # update requested to ordered
    page_form = 'summary'
    table_queries = tqc.TableQueryCollection('murray', page_form, table_name,
            {('name', 'status'):'requested'})
    table_queries.get_fields()
    first_table_query = table_queries.get_first()
    hidden_fields = {}
    hidden_fields['column_defaults'] = '{"status":2}'
    hidden_fields['button_text'] = 'Order Selected Oligos'
    # if nothing to display then page not found
    if not first_table_query.table_fields:
        abort(404)
    return templating.page_template('update',
            module_name = 'murray',
            table_name = table_name,
            table_query = first_table_query, hidden_fields = hidden_fields)

