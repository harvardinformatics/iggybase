from flask import request
from . import mod_core
from iggybase.mod_auth.organization_access_control import OrganizationAccessControl


@mod_core.route('/search', methods=['GET', 'POST'])
def search():
    table_object = request.args.get('table_object')
    property_name = request.args.get('property_name')
    field_name = request.args.get('field_name')
    input_id = request.args.get('input_id')
    table_name = table_object.replace("_", " ").title()

    oac = OrganizationAccessControl("core")
    search_fields = oac.get_search_field_data(table_object)

    modal_html = '<div class="modal-header">'
    modal_html += '<button type="button" class="close" data-dismiss="modal">&times;</button>'
    modal_html += '<h4 class="modal-title">' + table_name + ' Search</h4>'
    modal_html += '</div>'
    modal_html += '<div class="modal-body">'
    modal_html += '<input id="input_id" value="' + input_id + '" type="hidden">'
    modal_html += '<input id="property_id" value="' + property_name + '" type="hidden">'
    modal_html += '<input id="table_object" value="' + table_object + '" type="hidden">'
    modal_html += '<input id="field_name" value="' + field_name + '" type="hidden">'
    modal_html += '<p>All search inputs can use partial values</p>'
    modal_html += '</div>'

    return modal_html
