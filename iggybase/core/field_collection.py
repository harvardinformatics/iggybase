import operator
from collections import OrderedDict
from iggybase import utilities as util
from .field import Field
import logging

class FieldCollection:
    def __init__ (self, table_query_id, table_name = None):
        self.table_name = table_name
        self.table_query_id = table_query_id
        self.date_fields = {}
        self.rac = util.get_role_access_control()
        self.fields = self._populate_fields()
        self.fields_by_id = {}

    def _get_fields(self):
        field_res = self.rac.table_query_fields(
            self.table_query_id,
            self.table_name
        )
        return field_res

    def _populate_fields(self):
        table_fields = self._get_fields()
        field_dict = OrderedDict()
        for order, row in enumerate(table_fields):
            table_query_field = getattr(row, 'TableQueryField', None)
            calculation = getattr(row, 'TableQueryCalculation', None)
            field = Field(row.Field,
                    row.TableObject, order, table_query_field,
                    calculation)
            field_dict[field.display_name] = field

            if field.type == 4:
                self.date_fields[field.display_name] = order
        return field_dict

    def set_fk_fields(self):
        for field_name, field in self.fields.items():
            if field.is_foreign_key:
                # when possible reuse the same field to avoid extra queries, this is great when a query has
                # many long text for example
                if (field.Field.foreign_key_table_object_id, field.Field.foreign_key_display) in self.fields_by_id:
                    field.set_fk_field(self.fields_by_id[(field.Field.foreign_key_table_object_id, field.Field.foreign_key_display)])
                else:
                    field.set_fk_field()
            if field.Field.field_name == 'name':
                field_id_or_name = 'name'
            else:
                field_id_or_name = field.Field.id
            self.fields_by_id[(field.TableObject.id, field_id_or_name)] = field
