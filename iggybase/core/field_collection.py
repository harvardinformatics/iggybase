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
        self.fields_by_id = {}
        self.fk_field_objs = {} # for setting fk_field
        self.criteria = criteria
        self.role_filter = role_filter # used to ignore role for FK search
        # check if table_name extends
        self.extends_table_name = self.extends_table_name(self.table_name)

        # get all the fields
        self.fields = self._populate_fields()
        self.order_by = self.get_order_by()

    def __iter__(self):
        return iter(self.fields)

    def __getitem__(self, field_name):
        return self.fields[field_name]

    def keys(self):
        return self.fields.keys()

    def items(self):
        return self.fields.items()

    def values(self):
        return self.fields.values()

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
                    getattr(row, 'extension', None),
                    row.FieldRole,
                    row.DataType,
                    order,
                    table_query_field,
                    calculation)
            field_dict[field.name] = field
            # Table collection needs this
            self.fields_by_id[(row.TableObject.id, row.Field.id)] = field

            if field.type == 'datetime':
                self.date_fields[field.display_name] = order
        return field_dict

    def get_order_by(self):
        order_by = {}
        for name, field in self.fields.items():
            if field.order_by != None:
                order_by[name] = {
                    'order': abs(field.order_by),
                    'desc': (True if field.order_by < 0 else False)
                }
        order_by_sorted = OrderedDict(sorted(order_by.items(), key=lambda x:
            x[1]['order']))
        return order_by_sorted

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

    def get_fk_field_obj(self, field):
        fk_field = None
        # when possible reuse the same field to avoid extra queries, this is great when a query has
        # many long text for example
        if (field.Field.foreign_key_table_object_id, field.Field.foreign_key_display) in self.fk_field_objs:
            fk_field = self.fk_field_objs[(field.Field.foreign_key_table_object_id, field.Field.foreign_key_display)]
        else:
            fk_to = field.Field.foreign_key_table_object_id
            if fk_to:
                if field.Field.foreign_key_display:
                    criteria = {'id': field.Field.foreign_key_display}
                    fk_display = field.Field.foreign_key_display
                else:
                    criteria = {'display_name': 'name'}
                    fk_display = None
                fk_field = self.rac.table_query_fields(
                    None,
                    None,
                    fk_to,
                    criteria,
                    # we don't need role on fk table or field
                    role_filter = False
                )
                if fk_field:
                    fk_field = fk_field[0]
                    self.fk_field_objs[(fk_field.TableObject.id, fk_display)] = fk_field
        return fk_field

    def set_fk_fields(self):
        for field in self.fields.values():
            if field.is_foreign_key:
                field_obj = self.get_fk_field_obj(field)
                field.set_fk_field(field_obj)

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
