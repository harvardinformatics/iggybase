from flask import request, g
from collections import OrderedDict
from iggybase import utilities as util
from iggybase import g_helper
from .field_collection import FieldCollection

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, id, order, display_name, table_name = None, criteria = {}):
        self.id = id
        self.order = order
        self.display_name = display_name
        self.table_name = table_name
        self.table_dict = {} # results indexed by row id and field display_name
        self.criteria = criteria
        self.rac = g_helper.get_role_access_control()
        # fields will be decided with id or table_name
        self.fc = FieldCollection(id, table_name)

    def get_results(self):
        """ calls several class functions and returns results
        """
        self.fc.set_fk_fields()
        results = []
        self.criteria = self._add_table_query_criteria(self.criteria)
        self.oac = g_helper.get_org_access_control()
        self.results = self.oac.get_table_query_data(
                self.fc.fields,
                self.criteria
        )
        return self.results

    def _add_table_query_criteria(self, orig_criteria):
        criteria = {}
        # add criteria from get params
        filters = util.get_filters()
        for key, val in filters.items():
            if key in self.fc.fields:
                field = self.fc.fields[key]
                criteria_key = (field.TableObject.name, field.Field.display_name)
                criteria[criteria_key] = val
        # add criteria from db
        res = self.rac.table_query_criteria(
            self.id
        )
        for row in res:
            criteria_key = (row.TableObject.name, row.Field.display_name)
            criteria[criteria_key] = row.TableQueryCriteria.value

        criteria.update(orig_criteria)
        return criteria

    def format_results(self, add_row_id = True, allow_links = True):
        """Formats data
        - transforms into dictionary
        - adds links
        - calculates calculated fields
        - skips invisible fields, this must be done after data is retreived in
          cases where invisible fields are used in calculations
        """
        if self.results:
            keys = self.results[0].keys()

        # keep track of special fields
        link_fields = {}
        calc_fields = []
        invisible_fields = []
        url_root = request.url_root
        for field in self.fc.fields.values():
            if field.link_visible() and allow_links:
                link_fields[field.display_name] = self.get_link(url_root, 'detail', field.TableObject.name)
            if field.is_calculation():
                calc_fields.append(field.display_name)
            if not field.visible:
                invisible_fields.append(field.display_name)

        # create dictionary for each row
        for i, row in enumerate(self.results):
            row_dict = OrderedDict()
            for i, col in enumerate(row):
                name = keys[i]

                # set column value
                if name == 'DT_RowId':
                    dt_row_id = col
                    if not add_row_id:
                        continue
                elif name in invisible_fields:
                    continue
                elif name in calc_fields:
                        col = self.fc.fields[name].calculate(col, row,
                                keys)
                elif name in link_fields and col:
                    col_str = str(col)
                    col = ('<a href="' + link_fields[name] + col_str + '">' +
                            col_str + '</a>')

                row_dict[name] = col
            if row_dict:
                # store values as a dict of dict so we can access any of the
                # data by row_id and field display_name
                self.table_dict[dt_row_id] = row_dict

    def get_link(self, url_root, page = None, table = None):
        link = url_root + g.facility + '/' + 'core'
        if page:
            link += '/' + page
        if table:
            link += '/' + table + '/'
        return link

    def get_list_of_list(self): # for download
        table_list = []
        keys = list(self.get_first().keys())
        table_list.append(keys)
        for row in self.table_dict.values():
            table_list.append(list(row.values()))
        return table_list

    def get_first(self): # for detail
        return self.get_row_list()[0]

    def get_row_list(self): # for summary_ajax
        return list(self.table_dict.values())

    def update_and_get_message(self, updates, ids, message_fields):
        updated = self.oac.update_table_rows(updates, ids, self.display_name)
        updated_info = []
        for i in updated:
            # for each row grab any message_fields, to inform the user about the
            # update
            row_fields = []
            for field in message_fields:
                val = self.table_dict[i][field]
                if val:
                    row_fields.append(str(val))
            if row_fields:
                updated_info.append(', '.join(row_fields))
            else:
                updated_info.append('no ' + ', '.join(message_fields) + ' for id = ' + str(i))
        return updated_info
