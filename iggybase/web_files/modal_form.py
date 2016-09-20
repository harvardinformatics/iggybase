from iggybase import g_helper
from iggybase.core.field_collection import FieldCollection
import logging


class ModalForm():
    def __init__(self, search_vals):
        self.search_vals = search_vals

    def search_results(self):
        oac = g_helper.get_org_access_control()

        input_id = self.search_vals['modal_input_id']
        table_name = self.search_vals['modal_table_object']
        display_name = self.search_vals['modal_field_name']
        search_table = self.search_vals['modal_search_table']

        # logging.info('input_id: ' + str(input_id))
        # logging.info('table_name: ' + str(table_name))
        # logging.info('display_name: ' + str(display_name))
        # logging.info('search_table: ' + str(search_table))

        search_params = {}
        fields = ['name']
        for key, value in self.search_vals.items():
            if key[:7] == 'search_':
                field_name = key[7:]
                if field_name != 'name' and field_name != 'by_field':
                    fields.append(field_name)
                if value != '':
                    search_params[field_name] = value

        # logging.info('search_params: ')
        # logging.info(search_params)

        criteria = {'display_name': display_name}
        fc = FieldCollection(None, table_name, criteria)
        fc.set_fk_fields()

        if search_table == '':
            search_table = fc.fields[table_name + "|" + display_name].FK_TableObject.name

        search_fc = FieldCollection(None, search_table)
        for row in search_fc.get_search_fields():
            if row.Field.display_name not in fields:
                fields.append(row.Field.display_name)

        search_ids = {}
        for table_field_name, search_field in search_fc.fields.items():
            search_ids[search_field.Field.id] = search_field.Field.display_name

        search_field = fc.fields[table_name + "|" + display_name].Field.foreign_key_display
        if search_field:
            search_field = search_ids[search_field]
        else:
            search_field = 'name'

        if search_field not in fields:
            fields.append(search_field)

        if 'by_field' in search_params:
            value = search_params['by_field']
            search_params = {search_field: value}

        # logging.info('search_field: ' + str(search_field))

        search_results = oac.get_search_results(search_table, search_params)

        modal_html = '<div class="modal-header">'
        modal_html += '<button type="button" class="close_modal">&times;</button>'
        modal_html += '<h4 class="modal-title">Search Results</h4>'
        modal_html += '</div>'
        modal_html += '<div class="modal-body">'
        modal_html += '<input id="modal_input_id" value="' + input_id + '" type="hidden">'
        modal_html += '<input id="modal_table_object" value="' + table_name + '" type="hidden">'
        modal_html += '<input id="modal_field_name" value="' + display_name + '" type="hidden">'
        modal_html += '<input id="modal_search_table" value="' + search_table + '" type="hidden">'
        modal_html += '<table class="table-sm table-striped"><tr>'

        for field in fields:
            modal_html += '<th>' + field.replace("_", " ").title() + '</th>'

        modal_html += '</tr>'

        if search_results is not None and len(search_params) != 0:
            for row in search_results:
                modal_html += '<tr>'
                for field in fields:
                    res = getattr(row, field)
                    if field == search_field:
                        modal_html += ('<td><input luid="' + input_id + '"class="search-results" type="button" ' +
                                       'val_id="' + str(row.id) + '" value="' + format(res) + '"></input></td>')
                    else:
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

    def search_form(self):
        criteria = {'display_name': self.search_vals['display_name']}
        fc = FieldCollection(None, self.search_vals['table_name'], criteria)
        fc.set_fk_fields()
        modal_html = '<div class="modal-header">'
        modal_html += '<button type="button" class="close_modal">&times;</button>'
        modal_html += '<h4 class="modal-title">' + self.search_vals['table_name'] + ' Search</h4>'
        modal_html += '</div>'
        modal_html += '<div class="modal-body">'
        modal_html += '<input id="modal_input_id" value="' + self.search_vals['input_id'] + '" type="hidden">'
        modal_html += '<input id="modal_table_object" value="' + self.search_vals['table_name'] + '" type="hidden">'
        modal_html += '<input id="modal_search_table" value="' + \
                      fc.fields[self.search_vals['field_key']].FK_TableObject.name + '" type="hidden">'
        modal_html += '<input id="modal_field_name" value="' + self.search_vals['display_name'] + '" type="hidden">'
        modal_html += '<p>All search inputs can use partial values</p>'
        modal_html += '<table>'
        field = fc.fields[self.search_vals['field_key']]
        role_filter = False # ignore role filter since this is for FK
        search_fc = FieldCollection(None, field.FK_TableObject.name, None,
                role_filter)
        for row in search_fc.get_search_fields():
            modal_html += '<tr><td><label>' + row.display_name + '</label></td>'
            modal_html += '<td><input id="search_' + row.Field.display_name + '"></input></td></tr>'

        modal_html += '</table>'
        modal_html += '</div>'

        return modal_html
