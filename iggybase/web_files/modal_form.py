from iggybase import g_helper
from iggybase.core.field_collection import FieldCollection
import json
import logging


class ModalForm():
    def __init__(self, search_vals):
        self.search_vals = search_vals

    def search_results(self):
        oac = g_helper.get_org_access_control()

        input_id = self.search_vals['input_id']
        table_name = self.search_vals['table_name']
        display_name = self.search_vals['display_name']
        modal_open = self.search_vals['modal_open']
        search_value = self.search_vals['value']


        # logging.info('input_id: ' + str(input_id))
        # logging.info('table_name: ' + str(table_name))
        # logging.info('display_name: ' + str(display_name))
        # logging.info('modal_open: ' + str(modal_open))

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

        if 'by_field' in self.search_vals and search_value != '':
            search_params = {search_field: search_value}

        # logging.info('search_table: ' + search_table)
        # logging.info('search_field: ' + str(search_field))

        # logging.info('final search_params: ')
        # logging.info(search_params)

        search_results = oac.get_search_results(search_table, search_params)

        # TODO: move html to a template and use render template
        modal_html = '<table class="table-sm table-striped"><tr>'

        for field in fields:
            modal_html += '<th>' + field.replace("_", " ").title() + '</th>'


        modal_html += '</tr>'
        results = []

        if search_results is not None and len(search_params) != 0:
            for row in search_results:
                modal_html += '<tr>'
                for field in fields:
                    res = getattr(row, field)
                    if field == search_field:
                        results.append([1, format(res), row.id])
                        modal_html += ('<td><input luid="' + input_id + '"class="search-results" type="button" ' +
                                       'val_id="' + str(row.id) + '" value="' + format(res) + '"></input></td>')
                    else:
                        if res is not None:
                            modal_html += '<td>' + format(res) + '</td>'
                        else:
                            modal_html += '<td></td>'

                modal_html += '</tr>'
        else:
            modal_html += '<tr><td><label>No Results Found</label></td></tr>'

        modal_html += '</table>'

        # logging.info(modal_html)
        # logging.info(results)

        if len(results) == 1 and not modal_open:
            return json.dumps(results[0])
        else:
            return json.dumps(modal_html)

    def search_form(self):
        criteria = {'display_name': self.search_vals['display_name']}
        fc = FieldCollection(None, self.search_vals['table_name'], criteria)
        fc.set_fk_fields()
        modal_html = '<div class="modal-header">'
        modal_html += '<button type="button" class="close_modal">&times;</button>'
        modal_html += ('<h4 class="modal-title">' + self.search_vals['table_name'].replace("_", " ").title() +
                       ' Search</h4>')
        modal_html += '</div>'
        modal_html += '<div id="search_body" class="search-body">'
        modal_html += '<input id="modal_search_table" value="' + \
                      fc.fields[self.search_vals['field_key']].FK_TableObject.name + '" type="hidden">'
        modal_html += '<input id="modal_input_id" value="' + self.search_vals['input_id'] + '" type="hidden">'
        modal_html += '<p>All search inputs can use partial values</p>'
        modal_html += '<table>'
        field = fc.fields[self.search_vals['field_key']]
        role_filter = False # ignore role filter since this is for FK
        search_fc = FieldCollection(None, field.FK_TableObject.name, None,
                role_filter)
        search_fc.set_fk_fields()
        # logging.info('self.search_vals[field_key]]: ' + str(self.search_vals['field_key']))
        # logging.info('field.Field.foreign_key_display: ' + str(field.Field.foreign_key_display))
        # logging.info('field.FK_Field.id: ' + str(field.FK_Field.id))

        fields = []
        for row in search_fc.get_search_fields():
            fields.append(row.Field.id);
            modal_html += '<tr><td><label>' + row.display_name + '</label></td>'
            # logging.info('row.Field.id: ' + str(row.Field.id))
            if row.Field.id == field.FK_Field.id:
                modal_html += ('<td><input id="search_' + row.Field.display_name + '" value="' +
                               self.search_vals['value'] + '"></input></td></tr>')
            else:
                modal_html += '<td><input id="search_' + row.Field.display_name + '"></input></td></tr>'

        if field.Field.foreign_key_display and field.Field.foreign_key_display not in fields:
            search_field_object = search_fc.fields_by_id[(field.Field.foreign_key_table_object_id,
                                                          field.Field.foreign_key_display)]
            modal_html += ('<tr><td><label>' + search_field_object.display_name + '</label></td>')
            modal_html += ('<td><input id="search_' + search_field_object.Field.display_name + '" value="' +
                           self.search_vals['value'] + '"></input></td></tr>')

        modal_html += '</table>'
        modal_html += '<div id="modal_top_buttons" class="modal-top-buttons"></div>'
        modal_html += '<div id="modal_search_results" class="modal-search-results"></div>'
        modal_html += '</div>'

        return modal_html
