from flask import request
from json import loads
from . import mod_core
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl
import logging

@mod_core.route('/search', methods=['GET', 'POST'])
def search():
    table_object = request.args.get('table_object')
    field_name = request.args.get('field_name')
    input_id = request.args.get('input_id')
    module = request.args.get('module')
    table_name = table_object.replace("_", " ").title()

    oac = OrganizationAccessControl("core")
    search_module, search_table, search_fields = oac.get_search_field_data(module, table_object, field_name)

    modal_html = '<div class="modal-header">'
    modal_html += '<button type="button" class="close" data-dismiss="modal">&times;</button>'
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
            modal_html += '<tr><td><label>' + row.FieldFacilityRole.display_name.replace("_", " ").title() + '</label></td>'
            modal_html += '<td><input id="search_' + row.Field.field_name + '"></input></td></tr>'
    else:
        modal_html += '<tr><td><label>'+field_name.replace("_", " ").title()+'</label></td>'
        modal_html += '<td><input id="search_name"></input></td></tr>'
    modal_html += '</table>'
    modal_html += '</div>'

    return modal_html

@mod_core.route('/search_results', methods=['GET', 'POST'])
def search_results():
    search_vals = loads(request.args.get('search_vals'))

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

    oac = OrganizationAccessControl('core')
    search_results = oac.get_search_results(search_module, search_table, search_params)

    modal_html = '<div class="modal-header">'
    modal_html += '<button type="button" class="close" data-dismiss="modal">&times;</button>'
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

    for field in fields:
        logging.info(field)

    if search_results and len(search_params) != 0:
        for row in search_results:
            modal_html += '<tr><td><input luid="'+input_id+'"class="search-results" type="button" value="' + row.name + '"></input></td>'
            for field in fields:
                if field!='name':
                    res = getattr(row,field)
                    if res is not None:
                        modal_html += '<td><label>' + res + '</label></td>'
                    else:
                        modal_html += '<td></td>'

            modal_html += '</tr>'
    else:
        modal_html += '<tr><td><label>No Results Found</label></td></tr>'

    modal_html += '</table>'
    modal_html += '</div>'

    return modal_html