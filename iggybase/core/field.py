from iggybase import utilities as util
from .calculation import get_calculation
import logging

class Field:
    def __init__ (self, field, table_object, field_role, table_object_role, order, table_query_field = None, calculation = None):
        self.Field = field
        self.TableObject = table_object
        self.FieldRole = field_role
        self.TableObjectRole = table_object_role
        self.TableQueryField = table_query_field
        self.TableQueryCalculation = calculation
        self.display_name = util.get_field_attr(self.Field, self.TableQueryField, 'display_name')
        self._role_access_control = util.get_role_access_control()
        self.calculation_fields = self._get_calculation_fields(calculation)
        self.type = self._get_type()
        self.is_foreign_key = (self.Field.foreign_key_table_object_id != None)
        self.is_title_field = (self.TableObject.name == self.display_name)
        self.order = order
        self.visible = self.is_visible()

    def is_calculation(self):
        return (self.TableQueryCalculation != None)

    def is_visible(self):
        if self.TableQueryField:
            visible = self.TableQueryField.visible
        else:
            visible = self.FieldRole.visible
        if not visible:
            visible = False
        return visible

    def set_fk_field(self, fk_field = None):
        if not fk_field:
            fk_to = self.Field.foreign_key_table_object_id
            if fk_to:
                if self.Field.foreign_key_display:
                    fk_field = self._role_access_control.table_query_fields(
                            None,
                            None,
                            fk_to,
                            None,
                            self.Field.foreign_key_display
                        )
                else:
                    fk_field = self._role_access_control.table_query_fields(
                            None,
                            None,
                            fk_to,
                            'name' # if fk then we want the human readable name
                        )
                if fk_field:
                    fk_field = fk_field[0]
        if fk_field:
            self.fk_field = self.Field # field to which this is fk
            self.fk_table = self.TableObject
            self.Field = fk_field.Field
            self.TableObject = fk_field.TableObject
            self.FieldRole = fk_field.FieldRole
            self.TableObjectRole = fk_field.TableObjectRole
        else:
            self.is_foreign_key = False # maybe no role access

    def _get_type(self):
        # TODO: get some constants and caching working and return a constant
        # that the receiving class can use for comparisons
        return self.Field.data_type_id

    def _get_calculation_fields(self, calculation):
        calc_fields = {}
        if calculation:
            res = self._role_access_control.calculation_fields(
                    calculation.id
            )
            for row in res:
                calc_fields[self.display_name] = row
        return calc_fields

    def calculate(self, col, row, keys):
        cols = [col]
        func = self.TableQueryCalculation.function
        for name, field in self.calculation_fields.items():
            if name in keys:
                cols.append(row[keys.index(name)])
        col = get_calculation(func, cols)
        return col

    def link_visible(self):
        return (not self.is_calculation() and
                (
                    (self.Field.field_name == 'name' and not self.is_foreign_key) or
                    self.is_title_field or
                    (
                        self.is_foreign_key and
                        self.TableObject.name != 'long_text' and
                        self.is_visible()
                    )
                )
            )
