from collections import OrderedDict
from flask import request
from iggybase.database import admin_db_session
from iggybase.mod_admin import models
from iggybase.mod_auth import organization_access_control as oac
from iggybase.mod_auth import facility_role_access_control as frac
import logging

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, module_name, table_name, page_form):
        # TODO: make table_name or id optional
        self.module_name = module_name
        self.module = 'mod_' + self.module_name
        self.table_name = table_name
        self.page_form = page_form
        self.tables = []
        self.facility_role_access_control = frac.FacilityRoleAccessControl()

    def get_results(self):
        """ calls several class functions and returns results
            TODO: is it good practice to group these or should the code which
            instantiats the object call them all?
        """
        results = []
        if self.facility_role_access_control.has_access('Module', self.module):
            self.table_queries = self.facility_role_access_control.table_queries(self.table_name, self.page_form)
            self.table_fields = self.get_table_query_fields(self.table_queries)
            self.ordered_fields = self.order_fields(self.table_fields)
            organization_access_control = oac.OrganizationAccessControl(self.module)
            results = organization_access_control.get_table_query_data(
                    self.table_fields
            )
        return results

    def get_table_query_fields(self, table_queries):
        accessible_table_queries = []
        for table in table_queries:
            self.tables.append(table.TableObject.name)
            fields = self.facility_role_access_control.table_query_fields(
                    table.TableQueryRender.table_query_id,
                    table.TableObject.id
            )
            accessible_table_queries.append({
                    'table_object':table.TableObject,
                    'fields':fields
            })

        return accessible_table_queries

    def get_criteria(self):
        """Get the table query to use
        """
        criteria = None
        return criteria

    def order_fields(self, table_fields):
        field_order = {}
        for table in table_fields:
            for row in table['fields']:
                field_order[row.TableQueryField.display_name] = row.TableQueryField.order
        return sorted(field_order, key=field_order.get)

    def order_results(self, results):
        ordered_results = []
        for row in results:
            sorted_row = OrderedDict(sorted(row.items(), key=lambda i:self.ordered_fields.index(i[0])))
            ordered_results.append(sorted_row)
        return ordered_results

    def format_data(self, results, for_download = False):
        """Formats data for summary or detail
        - transforms into dictionary
        - removes model objects sqlalchemy puts in
        - formats FK data and link
        - formats name link which goes to detail template
        """
        table_rows = []
        # format results as dictionary
        if results:
            keys = results[0].keys()
            # filter out any objects
            keys_to_skip = []
            for fk in self.tables:
                keys_to_skip.append(fk)
            # create dictionary for each row and for fk data
            for row in results:
                row_dict = {}
                for i, col in enumerate(row):
                    if keys[i].lower() not in keys_to_skip:
                        if 'fk|' in keys[i]:
                            if '|name' in keys[i]:
                                fk_metadata = keys[i].split('|')
                                if fk_metadata[2]:
                                    table = fk_metadata[2]
                                    if for_download:
                                        item_value = col
                                    else:
                                        item_value = {
                                            'text': col,
                                            # add link foreign key table summary
                                            'link': '/' + fk_metadata[1] \
                                                    + '/detail/' + table + '/' \
                                                    + str(col)
                                        }
                                    row_dict[table] = item_value
                        else:  # add all other colums to table_rows
                            if for_download:
                                item_value = col
                            else:
                                item_value = {'text': col}
                            row_dict[keys[i]] = item_value
                            # name column values will link to detail
                            if keys[i] == 'name' and not for_download:
                                row_dict[keys[i]]['link'] = '/' \
                                    + self.module_name + '/detail/' \
                                    + self.table_name + '/' + str(col)
                table_rows.append(row_dict)
        table_rows = self.order_results(table_rows)
        return table_rows
