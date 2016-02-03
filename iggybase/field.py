from iggybase.mod_auth import role_access_control as rac
from iggybase.mod_core import utilities as util
from iggybase.mod_core import calculation as calc
import logging

class Field:
    def __init__ (self, field, table_object, module, table_query_field = None, calculation = None):
        self.Field = field
        self.TableObject = table_object
        self.Module = module
        self.TableQueryField = table_query_field
        self.TableQueryCalculation = calculation
        self.display_name = util.get_field_attr(self.Field, self.TableQueryField, 'display_name')
        self._role_access_control = rac.RoleAccessControl()
        self.calculation_fields = self._get_calculation_fields(calculation)
        self.type = self._get_type()
        self.is_foreign_key = self._get_foreign_key_field()
        self.is_title_field = (self.TableObject.name == self.display_name)

    def is_calculation(self):
        return (self.TableQueryCalculation != None)

    def is_visible(self):
        visible = True
        if self.TableQueryField:
            visible = self.TableQueryField.visible
        return visible

    def _get_foreign_key_field(self):
        is_fk = False
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
                self.fk_field = self.Field # field to which this is fk
                self.fk_table = self.TableObject
                self.Field = fk_field[0].Field
                self.TableObject = fk_field[0].TableObject
                self.Module = fk_field[0].Module
                is_fk = True
        return is_fk

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

    def calculate(self, module, col, row, keys):
        cols = [col]
        func = self.TableQueryCalculation.function
        for name, field in self.calculation_fields.items():
            if name in keys:
                cols.append(row[keys.index(name)])
        col = calc.get_calculation(module,
            func, cols)
        return col
