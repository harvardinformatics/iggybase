from collections import OrderedDict
from iggybase import g_helper
from .field import Field
import logging

class FieldCollection:
    # either a table_name or a table_query_id must be supplied
    def __init__ (self, table_query_id = None, table_name = None, criteria = {}, role_filter = True):
        self.table_name = table_name
        self.table_query_id = table_query_id
        self.date_fields = {}
        self.rac = g_helper.get_role_access_control()
        self.fields_by_id = {} # for setting fk_field
        self.criteria = criteria
        self.role_filter = role_filter # used to ignore role for FK search

        # get all the fields
        self.fields = self._populate_fields()

    def _get_fields(self):
        field_res = self.rac.table_query_fields(
            self.table_query_id,
            self.table_name,
            None,
            self.criteria,
            self.role_filter
        )
        return field_res

    def _populate_fields(self):
        table_fields = self._get_fields()
        field_dict = OrderedDict()
        for order, row in enumerate(table_fields):
            table_query_field = getattr(row, 'TableQueryField', None)
            calculation = getattr(row, 'TableQueryCalculation', None)
            field = Field(row.Field,
                    row.TableObject,
                    row.FieldRole,
                    row.DataType,
                    order,
                    table_query_field,
                    calculation)
            field_dict[field.name] = field

            if field.type == 4:
                self.date_fields[field.display_name] = order
        return field_dict

    def set_fk_fields(self):
        for field in self.fields.values():
            if field.is_foreign_key:
                # when possible reuse the same field to avoid extra queries, this is great when a query has
                # many long text for example
                field_obj = None
                if (field.Field.foreign_key_table_object_id, field.Field.foreign_key_display) in self.fields_by_id:
                    field_obj = self.fields_by_id[(field.Field.foreign_key_table_object_id, field.Field.foreign_key_display)]
                field.set_fk_field(field_obj)
            self.fields_by_id[(field.TableObject.id, field.Field.id)] = field

    def set_defaults(self, fk_defaults = {}):
        for field in self.fields.values():
            field.set_default(fk_defaults)

    def get_search_fields(self):
        search_fields = []
        for field in self.fields.values():
            if field.FieldRole.search_field:
                search_fields.append(field)
        if not search_fields:
            name_key = self.table_name + '|name'
            search_fields.append(self.fields[name_key])
        return search_fields
