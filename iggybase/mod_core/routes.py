from flask import request, jsonify, abort
from flask.ext.security import login_required
from flask.ext import excel
import json
from . import mod_core
import iggybase.templating as templating
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
from iggybase.table_query_collection import TableQueryCollection

MODULE_NAME = 'core'

@mod_core.route( '/' )
@login_required
def default(facility_name):
    return templating.page_template('index.html')

@mod_core.route( '/summary/<table_name>/' )
@login_required
def summary(facility_name, table_name):
    page_form = template = 'summary'
    return build_summary(facility_name, page_form, table_name, template)

@mod_core.route( '/summary/<table_name>/ajax' )
@login_required
def summary_ajax(facility_name, table_name):
    return build_summary_ajax(facility_name, 'summary', table_name)

@mod_core.route( '/action_summary/<table_name>/' )
@login_required
def action_summary(facility_name, table_name):
    page_form = 'summary'
    template = 'action_summary'
    return build_summary(facility_name, page_form, table_name,
    template)

@mod_core.route( '/action_summary/<table_name>/ajax' )
@login_required
def action_summary_ajax(facility_name, table_name):
    page_form = 'summary'
    return build_summary_ajax(facility_name, page_form, table_name)

@mod_core.route( '/detail/<table_name>/<row_name>' )
@login_required
def detail(facility_name, table_name, row_name):
    page_form = template = 'detail'
    criteria = {(table_name, 'name'): row_name}
    tqc = TableQueryCollection(facility_name, MODULE_NAME, page_form,
            table_name, criteria)
    tqc.get_fields()
    tqc.get_results()
    tqc.format_results()
    hidden_fields = {'table': table_name, 'row_name': row_name}
    return templating.page_template(
        template,
        module_name=MODULE_NAME,
        table_name=table_name,
        row_name=row_name,
        table_queries=tqc,
        hidden_fields=hidden_fields
    )

@mod_core.route( '/summary/<table_name>/download/' )
@login_required
def summary_download( facility_name, table_name ):
    page_form = 'summary'
    for_download = True
    tqc = TableQueryCollection(facility_name, MODULE_NAME, page_form, table_name)
    tqc.get_fields()
    tqc.get_results()
    tqc.format_results(for_download)
    table_rows = tqc.get_first().table_rows
    csv = excel.make_response_from_records(table_rows, 'csv')
    return csv

@mod_core.route( '/ajax/update_table_rows/<table_name>', methods=['GET', 'POST'] )
@login_required
def update_table_rows(facility_name, table_name):
    updates = request.json['updates']
    message_fields = request.json['message_fields']
    ids = request.json['ids']
    oac = OrganizationAccessControl()
    updated = oac.update_table_rows(table_name, updates, ids, message_fields)
    return json.dumps({'updated': updated})

@mod_core.route('/search', methods=['GET', 'POST'])
def search():
    table_object = request.args.get('table_object')
    field_name = request.args.get('field_name')
    input_id = request.args.get('input_id')
    module = request.args.get('module')
    table_name = table_object.replace("_", " ").title()

    oac = OrganizationAccessControl()
    search_module, search_table, search_fields = oac.get_search_field_data(module, table_object, field_name)

    modal_html = '<div class="modal-header">'
    modal_html += '<button type="button" class="close_modal">&times;</button>'
    modal_html += '<h4 class="modal-title">' + table_name + ' Search</h4>'
    modal_html += '</div>'
    modal_html += '<div class="modal-body">'
    modal_html += '<input id="modal_input_id" value="' + input_id + '" type="hidden">'
    modal_html += '<input id="modal_table_object" value="' + table_object + '" type="hidden">'
    modal_html += '<input id="modal_search_table" value="' + search_table + '" type="hidden">'
    modal_html += '<input id="modal_field_name" value="' + field_name + '" type="hidden">'
    modal_html += '<input id="modal_module" value="' + module + '" type="hidden">'
    modal_html += '<input id="modal_search_module" value="' + search_module + '" type="hidden">'
    modal_html += '<p>All search inputs can use partial values</p>'
    modal_html += '<table>'
    if search_fields:
        for row in search_fields:
            modal_html += '<tr><td><label>' + row.FieldRole.display_name.replace("_", " ").title() + '</label></td>'
            modal_html += '<td><input id="search_' + row.Field.field_name + '"></input></td></tr>'
    else:
        modal_html += '<tr><td><label>'+field_name.replace("_", " ").title()+'</label></td>'
        modal_html += '<td><input id="search_name"></input></td></tr>'
    modal_html += '</table>'
    modal_html += '</div>'

    return modal_html

@mod_core.route('/search_results', methods=['GET', 'POST'])
def search_results():
    search_vals = json.loads(request.args.get('search_vals'))

    oac = OrganizationAccessControl()

    input_id = search_vals['modal_input_id']
    table_object = search_vals['modal_table_object']
    field_name = search_vals['modal_field_name']
    module = search_vals['modal_module']
    search_table = search_vals['modal_search_table']
    search_module = search_vals['modal_search_module']

    search_params = {}
    fields = []
    for key, value in search_vals.items():
        if key[:7]=='search_':
            fields.append(key[7:])
            if value !='':
                search_params[key[7:]] = value

    if search_table == '':
        search_module, search_table, search_fields = oac.get_search_field_data(module, table_object, field_name)

        for row in search_fields:
            if row.Field.field_name not in fields:
                fields.append(row.Field.field_name)

    search_results = oac.get_search_results(search_module, search_table, search_params)

    modal_html = '<div class="modal-header">'
    modal_html += '<button type="button" class="close_modal">&times;</button>'
    modal_html += '<h4 class="modal-title">Search Results</h4>'
    modal_html += '</div>'
    modal_html += '<div class="modal-body">'
    modal_html += '<input id="modal_input_id" value="' + input_id + '" type="hidden">'
    modal_html += '<input id="modal_table_object" value="' + table_object + '" type="hidden">'
    modal_html += '<input id="modal_field_name" value="' + field_name + '" type="hidden">'
    modal_html += '<input id="modal_module" value="' + module + '" type="hidden">'
    modal_html += '<input id="modal_search_module" value="' + search_module + '" type="hidden">'
    modal_html += '<input id="modal_search_table" value="' + search_table + '" type="hidden">'
    modal_html += '<table class="table-sm table-striped"><tr><td>Name</td>'

    for field in fields:
        if field!='name':
            modal_html += '<td>' + field.replace("_", " ").title() + '</td>'

    modal_html += '</tr>'

    if search_results is not None and len(search_params) != 0:
        for row in search_results:
            modal_html += '<tr><td><input luid="'+input_id+'"class="search-results" type="button" value="' + row.name + '"></input></td>'
            for field in fields:
                if field!='name':
                    res = getattr(row,field)
                    if res is not None:
                        modal_html += '<td><label>' + format(res) + '</label></td>'
                    else:
                        modal_html += '<td></td>'

            modal_html += '</tr>'
    else:
        modal_html += '<tr><td><label>No Results Found</label></td></tr>'

    modal_html += '</table>'
    modal_html += '</div>'

    return modal_html

def build_summary(facility_name, page_form, table_name, template):
    tqc = TableQueryCollection(facility_name, MODULE_NAME, page_form, table_name)
    tqc.get_fields()
    first_table_query = tqc.get_first()
    # if nothing to display then page not found
    if not first_table_query.table_fields:
        abort(404)
    return templating.page_template(template,
            module_name = MODULE_NAME,
            table_name = table_name,
            table_query = first_table_query)

def build_summary_ajax(facility_name, page_form, table_name):
    tqc = TableQueryCollection(facility_name, MODULE_NAME, page_form, table_name)
    tqc.get_fields()
    tqc.get_results()
    tqc.format_results()
    table_query = tqc.get_first()
    json_rows = table_query.get_json()
    return jsonify({'data':json_rows})
