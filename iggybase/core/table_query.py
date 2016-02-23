from collections import OrderedDict
from flask import request, g
from iggybase.auth import organization_access_control as oac
from iggybase.auth import role_access_control as rac
from iggybase import utilities as util
from .field import Field as field_class

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, id, order, display_name, facility_name, table_name = None, criteria = {}, row_id = False):
        self.id = id
        self.order = order
        self.display_name = display_name
        self.facility_name = facility_name
        self.table_name = table_name
        self.table_rows = []
        self.field_dict = OrderedDict()
        self._role_access_control = rac.RoleAccessControl()
        self.criteria = criteria
        self.date_fields = {}
        self.table_fields = []
        self.row_id = row_id

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
                self.field_dict,
                self.criteria,
                self.row_id
        )
        return self.results

    def _get_table_query_fields(self):
        table_query_fields = self._role_access_control.table_query_fields(
            self.id,
            self.table_name
        )
        return table_query_fields

    def _add_table_query_criteria(self, orig_criteria):
        criteria = {}
        # add criteria from get params
        filters = util.get_filters()
        for key, val in filters.items():
            if key in self.field_dict:
                field = self.field_dict[key]
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
            table_query_field = getattr(row, 'TableQueryField', None)
            calculation = getattr(row, 'TableQueryCalculation', None)
            field = field_class(row.Field,
                    row.TableObject, table_query_field,
                    calculation)
            field_dict[field.display_name] = field
        return field_dict

    def _get_date_fields(self, field_dict):
        date_fields = {}
        for i, field in enumerate(field_dict.values()):
            if field.type == 4:# TODO: user constant
                date_fields[field.display_name] = i
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
                visible = True
                if keys[i] in self.field_dict:
                    field = self.field_dict[keys[i]]
                    visible = field.is_visible()
                    calculation = field.is_calculation()
                    if calculation:
                        col = field.calculate(col, row,
                                keys)
                if visible:
                    if for_download:
                        item_value = col
                    else:
                        item_value = {'text': col}
                    row_dict[keys[i]] = item_value
                    # name and table title columns values will link to detail
                    if (not for_download and self.link_visible(field)):
                        row_dict[keys[i]]['link'] = self.get_link(
                            col,
                            self.facility_name,
                            g.module,
                            request.url_root,
                            'detail',
                            field.TableObject.name
                        )
            self.table_rows.append(row_dict)

    def link_visible(self, field):
        return (not field.is_calculation() and
                (
                    field.Field.field_name == 'name' or
                    field.is_title_field or
                    (
                        field.is_foreign_key and
                        field.TableObject.name != 'long_text'
                    )
                )
            )

    def get_link(self, value, facility, module, url_root, page = None, table = None):
        link = url_root + facility + '/' + module
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
