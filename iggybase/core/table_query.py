from flask import request, g
from collections import OrderedDict
from iggybase.auth.organization_access_control import OrganizationAccessControl
from iggybase import utilities as util
from .field_collection import FieldCollection
from iggybase.admin import models as admin_models

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, id, order, display_name, table_name = None, criteria = {}):
        self.id = id
        self.order = order
        self.display_name = display_name
        self.table_name = table_name
        self.table_rows = OrderedDict()
        self.table_dict = []
        self.criteria = criteria
        self.rac = util.get_role_access_control()
        self.fields = FieldCollection(id, table_name)

    def get_results(self):
        """ calls several class functions and returns results
        """
        self.fields.set_fk_fields()
        results = []
        self.criteria = self._add_table_query_criteria(self.criteria)
        self.oac = OrganizationAccessControl()
        self.results = self.oac.get_table_query_data(
                self.fields.fields,
                self.criteria
        )
        return self.results

    def _add_table_query_criteria(self, orig_criteria):
        criteria = {}
        # add criteria from get params
        filters = util.get_filters()
        for key, val in filters.items():
            if key in self.fields.fields:
                field = self.fields.fields[key]
                criteria_key = (field.TableObject.name, field.Field.field_name)
                criteria[criteria_key] = val
        # add criteria from db
        res = self.rac.table_query_criteria(
            self.id
        )
        for row in res:
            criteria_key = (row.TableObject.name, row.Field.field_name)
            criteria[criteria_key] = row.TableQueryCriteria.value

        criteria.update(orig_criteria)
        return criteria

    def format_results(self, add_row_id = True, allow_links = True):
        """Formats data for summary or detail
        - transforms into dictionary
        - removes model objects sqlalchemy puts in
        - formats FK data and link
        - formats name link which goes to detail template
        """
        # format results as dictionary
        if self.results:
            keys = self.results[0].keys()
        link_fields = {}
        calc_fields = []
        invisible_fields = []
        url_root = request.url_root
        col_names = {}
        col_count = 0
        for field_name, field in self.fields.fields.items():
            if field.link_visible() and allow_links:
                link_fields[field_name] = self.get_link(url_root, 'detail', field.TableObject.name)
            if field.is_calculation():
                calc_fields.append(field_name)
            if not field.visible:
                invisible_fields.append(field_name)
            else:
                col_names[field_name] = str(col_count)
                col_count += 1
        col_names['DT_RowId'] = 'DT_RowId'
        # create dictionary for each row and for fk data
        for i, row in enumerate(self.results):
            row_dict = OrderedDict()
            row_by_order = {}
            for i, col in enumerate(row):
                name = keys[i]
                if name == 'DT_RowId':
                    dt_row_id = col
                    if not add_row_id:
                        continue
                elif name in invisible_fields:
                    continue
                else:
                    if name in calc_fields:
                        col = self.fields.fields[name].calculate(col, row,
                                keys)
                if name in link_fields and col:
                    col_str = str(col)
                    item_value = ('<a href="' + link_fields[name] + col_str + '">' +
                            col_str + '</a>')
                else:
                    item_value = col
                row_by_order[col_names[name]] = item_value
                row_dict[name] = item_value
            if row_by_order:
                self.table_rows[dt_row_id] = row_by_order
                self.table_dict.append(row_dict)

    def get_link(self, url_root, page = None, table = None):
        link = url_root + g.facility + '/' + 'core'
        if page:
            link += '/' + page
        if table:
            link += '/' + table + '/'
        return link

    def get_first(self):
        '''first = OrderedDict()
        try:
            vals = list(self.table_rows.values())[0]
            for field_name, field in self.fields.fields.items():
                first[field_name] = vals[str(field.order)]
        except:
            first = {}'''
        first = self.table_dict[0]
        return first

    def update_and_get_message(self, updates, ids, message_fields):
        updated = self.oac.update_table_rows(updates, ids, self.display_name)
        updated_info = []
        for i in updated:
            # for each row grab any message_fields, to inform the user about the
            # update
            row_fields = []
            for field in message_fields:
                if field.startswith('plaintext|'):
                    row_fields.append(str(field.replace('plaintext|', '')))
                else:
                    row_fields.append(str(self.table_rows[i][str(self.fields.fields[field.replace('_', ' ')].order)]))
            if row_fields:
                updated_info.append(', '.join(row_fields))
        return updated_info
