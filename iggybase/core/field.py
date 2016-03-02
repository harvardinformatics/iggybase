from iggybase.auth import role_access_control as rac
from iggybase import utilities as util
from .calculation import get_calculation
import logging

class Field:
    def __init__ (self, field, table_object, order, table_query_field = None, calculation = None):
        self.Field = field
        self.TableObject = table_object
        self.TableQueryField = table_query_field
        self.TableQueryCalculation = calculation
        self.display_name = util.get_field_attr(self.Field, self.TableQueryField, 'display_name')
        self._role_access_control = rac.RoleAccessControl()
        self.calculation_fields = self._get_calculation_fields(calculation)
        self.type = self._get_type()
        self.is_foreign_key = (self.Field.foreign_key_table_object_id != None)
        self.is_title_field = (self.TableObject.name == self.display_name)
        self.order = order

    def is_calculation(self):
        return (self.TableQueryCalculation != None)

    def is_visible(self):
        visible = True
        if self.TableQueryField:
            visible = self.TableQueryField.visible
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
                fk_field = fk_field[0]
        if fk_field:
            self.fk_field = self.Field # field to which this is fk
            self.fk_table = self.TableObject
            self.Field = fk_field.Field
            self.TableObject = fk_field.TableObject

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
