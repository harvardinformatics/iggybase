from collections import OrderedDict
from flask import request
from iggybase.mod_auth import organization_access_control as oac
from iggybase.mod_auth import role_access_control as rac
from iggybase.mod_core import utilities as util
import logging

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, id, order, display_name, module_name, table_name = None, criteria = {}):
        self.id = id
        self.order = order
        self.display_name = display_name
        self.module_name = module_name
        self.module = 'mod_' + module_name
        self.table_name = table_name
        self.table_rows = []
        self.field_dict = OrderedDict()
        self._role_access_control = rac.RoleAccessControl()
        self.criteria = criteria
        self.date_fields = {}
        self.table_fields = []

    def get_fields(self):
        self.table_fields = self._get_table_query_fields()
        # get display names and set results as an ordered dict
        self.field_dict = self._get_field_dict(self.table_fields)
        self.date_fields = self._get_date_fields(self.field_dict)

    def get_results(self):
        """ calls several class functions and returns results
        """
        results = []
        self.criteria = self._add_table_query_criteria(self.criteria)
        organization_access_control = oac.OrganizationAccessControl()
        self.results = organization_access_control.get_table_query_data(
                self.table_fields,
                self.criteria
        )
        return self.results

    def _get_table_query_fields(self):
        table_query_fields = self._role_access_control.table_query_fields(
            self.id,
            self.table_name
        )
        return table_query_fields

    def _get_filters(self):
        req = dict(request.args)
        filters = {}
        if 'search' in req:
            search = dict(request.args)['search'][0].replace('?', '')
            if search:
                search = search.split('&')
                for param in search:
                    pair = param.split('=')
                    filters[pair[0]] = pair[1]
        return filters

    def _add_table_query_criteria(self, orig_criteria):
        criteria = {}
        # add criteria from get params
        filters = self._get_filters()
        for key, val in filters.items():
            if key in self.field_dict:
                field = self.field_dict[key]
                if field.Field.foreign_key_table_object_id:
                    filter_fields = self._role_access_control.table_query_fields(
                        None,
                        None,
                        field.Field.foreign_key_table_object_id,
                        'name' # if fk then we want the human readable name
                    )
                    if filter_fields:
                        filter_field = filter_fields[0]
                        criteria_key = (filter_field.TableObject.name, filter_field.Field.field_name)
                        criteria[criteria_key] = val
                else:
                    criteria_key = (field.TableObject.name, field.Field.field_name)
                    criteria[criteria_key] = val
        # add criteria from db
        res = self._role_access_control.table_query_criteria(
            self.id
        )
        for row in res:
            criteria_key = (row.TableObject.name, row.Field.field_name)
            criteria[criteria_key] = row.TableQueryCriteria.value

        criteria.update(orig_criteria)
        return criteria

    def _get_field_dict(self, table_fields):
        field_dict = OrderedDict()
        for row in table_fields:
            display_name = util.get_field_attr(row, 'display_name')
            field_dict[display_name] = row
        return field_dict

    def _get_date_fields(self, field_dict):
        date_fields = {}
        index = 0
        for name, field in field_dict.items():
            if field.Field.data_type_id == 4:
                date_fields[name] =  index
            index += 1
        return date_fields

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
            row_dict = OrderedDict()
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
                                    request.url_root,
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
                    # name and table title columns values will link to detail
                    if keys[i] in self.field_dict:
                        table_name = self.field_dict[keys[i]].TableObject.name
                        is_title_field = (keys[i] == table_name)
                    else:
                        is_title_field = False
                    if (
                            not for_download and
                            (
                                keys[i] == 'name' or
                                is_title_field
                            )
                        ):
                        row_dict[keys[i]]['link'] = self.get_link(
                            col,
                            self.module_name,
                            request.url_root,
                            'detail',
                            table_name
                        )
            self.table_rows.append(row_dict)

    def get_link(self, value, module, url_root, page = None, table = None):
        link = url_root + module
        if page:
            link += '/' + page
        if table:
            link += '/' + table
        link += '/' + str(value)
        return link

    def get_first(self):
        try:
            first = self.table_rows[0]
        except:
            first = {}
        return first

    def get_json(self):
        list_rows = []
        for row in self.table_rows:
            list_row = OrderedDict()
            col_num = 0
            for key, val in row.items():
                formatted_val = ''
                if 'text' in val:
                    if 'link' in val:
                        formatted_val = ('<a href="' + str(val['link']) + '">' +
                            str(val['text']) + '</a>')
                    else:
                        formatted_val = str(val['text'])
                if (key == 'DT_RowId'):
                    list_row[key] = formatted_val
                else:
                    list_row[str(col_num)] = formatted_val
                    col_num += 1
            list_rows.append(list_row)
        return list_rows
