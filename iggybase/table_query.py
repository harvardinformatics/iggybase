from collections import OrderedDict
from flask import request
from iggybase.database import admin_db_session
from iggybase.mod_admin import models
from iggybase.mod_auth import organization_access_control as oac
from iggybase.mod_auth import facility_role_access_control as frac
from iggybase.mod_core import utilities as util
import logging

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, id, order, display_name, module_name, table_name = None):
        self.id = id
        self.order = order
        self.display_name = display_name
        self.module_name = module_name
        self.module = 'mod_' + module_name
        self.table_name = table_name
        self.table_rows = []
        self._facility_role_access_control = frac.FacilityRoleAccessControl()

    def get_results(self):
        """ calls several class functions and returns results
        """
        results = []
        self.table_fields = self._get_table_query_fields()
        self.criteria = self._get_table_query_criteria()
        self._ordered_fields = self._get_field_order(self.table_fields)
        organization_access_control = oac.OrganizationAccessControl(self.module)
        self.results = organization_access_control.get_table_query_data(
                self.table_fields,
                self.criteria
        )
        return self.results

    def _get_table_query_fields(self):
        table_query_fields = self._facility_role_access_control.table_query_fields(
            self.id,
            self.table_name
        )
        return table_query_fields

    def _get_table_query_criteria(self):
        criteria = []
        res = self._facility_role_access_control.table_query_criteria(
            self.id
        )
        for row in res:
            col = util.get_column(
                row.Module.name,
                row.TableObject.name,
                row.Field.field_name
            )
            criteria.append(
                col == row.TableQueryCriteria.value
            )
        return criteria

    def _get_field_order(self, table_fields):
        self.field_dict = {}
        for row in table_fields:
            display_name = util.get_field_attr(row.TableQueryField, row.Field, 'display_name')
            self.field_dict[display_name] = row
        # return a sorted list of field names
        return sorted(
                self.field_dict,
                key=lambda i:
                    util.get_field_attr(
                        self.field_dict[i].TableQueryField,
                        self.field_dict[i].Field,
                        'order'
                    )
        )

    def _order_fields(self, row):
        return OrderedDict(sorted(row.items(), key=lambda i:self._ordered_fields.index(i[0])))

    def format_results(self, for_download = False):
        """Formats data for summary or detail
        - transforms into dictionary
        - removes model objects sqlalchemy puts in
        - formats FK data and link
        - formats name link which goes to detail template
        """
        self.table_rows = []
        # format results as dictionary
        if self.results:
            keys = self.results[0].keys()
        # create dictionary for each row and for fk data
        for row in self.results:
            row_dict = {}
            for i, col in enumerate(row):
                if 'fk|' in keys[i]:
                    fk_metadata = keys[i].split('|')
                    if fk_metadata[2]:
                        table = fk_metadata[2]
                        field = fk_metadata[3]
                        if for_download:
                            item_value = col
                        else:
                            item_value = {
                                'text': col,
                                # add link foreign key table summary
                                'link': self.get_link(
                                    col,
                                    fk_metadata[1],
                                    'detail',
                                    table
                                )
                            }
                        row_dict[field] = item_value
                else:  # add all other colums to table_rows
                    if for_download:
                        item_value = col
                    else:
                        item_value = {'text': col}
                    row_dict[keys[i]] = item_value
                    # name column values will link to detail
                    if keys[i] == 'name' and not for_download:
                        table_name = self.field_dict[keys[i]].TableObject.name
                        row_dict[keys[i]]['link'] = self.get_link(
                            col,
                            self.module_name,
                            'detail',
                            table_name
                        )
            self.table_rows.append(self._order_fields(row_dict))

    def get_link(self, value, module, page = None, table = None):
        link = '/' + module
        if page:
            link += '/' + page
        if table:
            link += '/' + table
        link += '/' + str(value)
        return link

    def get_first(self):
        first = {};
        if self.table_rows[0]:
            first = self.table_rows[0]
        return first
