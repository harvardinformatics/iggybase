from collections import OrderedDict
from flask import request, g
from iggybase.auth import organization_access_control as oac
from iggybase.auth import role_access_control as rac
from iggybase import utilities as util
from .field import Field as field_class
from iggybase.admin import models as admin_models

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, id, order, display_name, facility_name, table_name = None, criteria = {}):
        self.id = id
        self.order = order
        self.display_name = display_name
        self.facility_name = facility_name
        self.table_name = table_name
        self.table_rows = {}
        self.field_dict = OrderedDict()
        self._role_access_control = rac.RoleAccessControl()
        self._org_access_control = oac.OrganizationAccessControl()
        self.criteria = criteria
        self.date_fields = {}
        self.table_fields = []

    def get_fields(self):
        self.table_fields = self._get_table_query_fields()
        # get display names and set results as an ordered dict
        self.field_dict = self._get_field_dict(self.table_fields)

    def get_results(self):
        """ calls several class functions and returns results
        """
        self._set_fk_fields(self.field_dict)
        results = []
        self.criteria = self._add_table_query_criteria(self.criteria)
        self.results = self._org_access_control.get_table_query_data(
                self.field_dict,
                self.criteria
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
        for order, row in enumerate(table_fields):
            table_query_field = getattr(row, 'TableQueryField', None)
            calculation = getattr(row, 'TableQueryCalculation', None)
            field = field_class(row.Field,
                    row.TableObject, order, table_query_field,
                    calculation)
            field_dict[field.display_name] = field

            if field.type == 4:
                self.date_fields[field.display_name] = order
        return field_dict

    def _set_fk_fields(self, field_dict):
        fields_by_id = {}
        for field_name, field in field_dict.items():
            if field.is_foreign_key:
                if (field.Field.foreign_key_table_object_id, field.Field.foreign_key_display) in fields_by_id:
                    field.set_fk_field(fields_by_id[(field.Field.foreign_key_table_object_id, field.Field.foreign_key_display)])
                else:
                    field.set_fk_field()
            if field.Field.field_name == 'name':
                field_id_or_name = 'name'
            else:
                field_id_or_name = field.Field.id
            fields_by_id[(field.TableObject.id, field_id_or_name)] = field

    def format_results(self, for_download = False):
        """Formats data for summary or detail
        - transforms into dictionary
        - removes model objects sqlalchemy puts in
        - formats FK data and link
        - formats name link which goes to detail template
        """
        url_root = request.url_root
        # format results as dictionary
        if self.results:
            keys = self.results[0].keys()
        link_fields = []
        calc_fields = []
        col_names = {}
        for field_name, field in self.field_dict.items():
            if self.link_visible(field):
                link_fields.append(field_name)
            if field.is_calculation():
                calc_fields.append(field_name)
            col_names[field_name] = str(field.order)
            col_names['DT_RowId'] = 'DT_RowId'

        # create dictionary for each row and for fk data
        for i, row in enumerate(self.results):
            row_dict = {}
            for i, col in enumerate(row):
                name = keys[i]
                if name == 'DT_RowId':
                    dt_row_id = col
                else:
                    if name in calc_fields:
                        col = self.field_dict[name].calculate(col, row,
                                keys)
                if name in link_fields and col:
                    # name and table title columns values will link to detail
                    link = self.get_link(
                        col,
                        self.facility_name,
                        g.module,
                        url_root,
                        'detail',
                        self.field_dict[name].TableObject.name
                    )
                    item_value = ('<a href="' + str(link) + '">' +
                            str(col) + '</a>')
                else:
                    item_value = col
                row_dict[col_names[name]] = item_value

            self.table_rows[dt_row_id] = row_dict

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

    def update_and_get_message(self, updates, ids, message_fields):
        updated = self._org_access_control.update_table_rows(updates, ids, self.table_name)
        updated_info = []
        for i in updated:
            # for each row grab any message_fields, to inform the user about the
            # update
            row_fields = []
            for field in message_fields:
                row_fields.append(str(self.table_rows[i][field]))
            if row_fields:
                updated_info.append(', '.join(row_fields))
        return updated_info
