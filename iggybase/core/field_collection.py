from collections import OrderedDict
import json
from iggybase import g_helper
from .field import Field
import logging

class FieldCollection:
    # either a table_name or a table_query_id must be supplied
    def __init__ (self, table_query_id = None, table_name = None, criteria = {}, role_filter = True):
        self.table_name = table_name
        self.table_names = [table_name]
        self.table_query_id = table_query_id
        self.date_fields = {}
        self.rac = g_helper.get_role_access_control()
        self.fields_by_id = {} # for setting fk_field
        self.criteria = criteria
        self.role_filter = role_filter # used to ignore role for FK search
        # check if table_name extends
        self.extends_table_name = self.extends_table_name(self.table_name)

        # get all the fields
        self.fields = self._populate_fields()

    def _get_fields(self):
        field_res = self.rac.table_query_fields(
            self.table_query_id,
            self.table_names,
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

            if field.type == 'datetime':
                self.date_fields[field.display_name] = order
        return field_dict

    def extends_table_name(self, table_name):
        # if extends table then add parent to self.table_names
        extends_table_name = None
        if table_name:
            table_object_row = self.rac.get_role_row('table_object', {'name': table_name})
            if table_object_row:
                extends = getattr(table_object_row.TableObject, 'extends_table_object_id')
                if extends:
                    extends_row = self.rac.get_role_row('table_object', {'id': extends})
                    if extends_row:
                        extends_table_name = getattr(extends_row.TableObject, 'name')
                        self.table_names.append(extends_table_name)
        return extends_table_name

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
        for tablefield_name, field in self.fields.items():
            if field.FieldRole.search_field:
                search_fields.append(field)

        logging.info(json.dumps(self.table_names) + ' self.fields: ')
        for key, value in self.fields.items():
            logging.info(key)

        if search_fields:
            return search_fields
        else:
            return [self.fields[(self.extends_table_name or self.table_name) + '|name']]
