from iggybase.mod_auth import role_access_control as rac
from iggybase.mod_core import utilities as util
from iggybase.mod_core import calculation as calc
import logging

class TableQueryField:
    def __init__ (self, field, table_object, module, calculation = None):
        self.Field = field
        self.TableObject = table_object
        self.Module = module
        self.TableQueryCalculation = calculation
        self._role_access_control = rac.RoleAccessControl()
        self.calculation_fields = self._get_calculation_fields(calculation)

    def is_calculation(self):
        return (self.TableQueryCalculation != None)

    def _get_calculation_fields(self, calculation):
        calc_fields = {}
        if calculation:
            res = self._role_access_control.calculation_fields(
                    calculation.id
            )
            for row in res:
                display_name = util.get_field_attr(row, 'display_name')
                calc_fields[display_name] = row
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
