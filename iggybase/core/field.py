from iggybase import g_helper
from flask import g
from .calculation import get_calculation
import datetime
import logging

class Field:
    def __init__ (self, field, table_object, field_role, data_type, order, table_query_field = None, calculation = None):
        self.Field = field
        self.TableObject = table_object
        self.FieldRole = field_role
        self.DataType = data_type

        # FK data will be set when set_fk_field is called
        self.FK_Field = None
        self.FK_TableObject = None
        self.FK_FieldRole = None

        self.DYN_TableObject = None
        self.DYN_Field_Definition = None

        # None if table_query by table_name rather than id
        self.TableQueryField = table_query_field
        self.TableQueryCalculation = calculation

        if calculation:
            # there are cases where we want to display calculated and
            # uncalculated values of a field so calculated fields need
            # a name unique from the uncalculated field
            self.name = 'calc|' + self.TableQueryField.name
        else:
            # unique name, table|field
            self.name = self.TableObject.name + '|' + self.Field.display_name
        self.display_name = self.get_field_display_name() # name from role or tq
        self.rac = g_helper.get_role_access_control()
        self.calculation_fields = self._get_calculation_fields(calculation)
        self.type = self._get_type()
        self.is_foreign_key = (self.Field.foreign_key_table_object_id is not None)
        self.is_dynamic_field = (self.Field.dynamic_field_definition_field_id is not None)
        self.is_title_field = (self.TableObject.id == self.Field.table_object_id and self.Field.display_name == 'name')
        self.order = self.get_field_order()

        # base visibility on original field, do not change if fk field
        self.visible = self.set_visiblity()

        # can be set by set_default()
        self.default = None

    def is_calculation(self):
        return (self.TableQueryCalculation != None)

    def set_visiblity(self):
        visible = False
        if self.TableQueryField:
            visible = self.TableQueryField.visible
        else:
            visible = self.FieldRole.visible
        return visible


    def set_default(self, fk_defaults):
        default = None
        # set fk_default if there is one
        if (self.is_foreign_key and self.FK_TableObject is not None
                and self.FK_TableObject.name in fk_defaults):
            default = fk_defaults[self.FK_TableObject.name]
        else: # set default from field
            if self.Field.default == 'now':
                default = datetime.datetime.utcnow()
            elif self.Field.default == 'today':
                default = datetime.date.today()
            elif self.Field.default == 'user':
                default = g.user.id
            elif self.Field.default == 'org':
                default = g.current_org_id
            # TODO: all trues should be stored at 1 but right now child and
            # grandchild tables only work with True, we should fix this once we
            # have a data_instance class
            elif self.Field.default == 'True':
                default = 1
            elif self.Field.default is not None:
                default = self.Field.default
        self.default = default

    def get_field_display_name(self):
        # this should be lowercase for consistancy, templates responsible for
        # capitalization of title displays
        if self.TableQueryField and getattr(self.TableQueryField, 'display_name'):
            display_name = getattr(self.TableQueryField, 'display_name')
        elif self.FieldRole.display_name:
            display_name = self.FieldRole.display_name
        elif self.Field.display_name:
            display_name = self.Field.display_name
        else:
            return 'WHOA! Something is not right here. There is no display name for field ' + self.Field.name + "."
        return display_name.replace('_', ' ').title()

    def get_field_order(self):
        if self.TableQueryField and self.TableQueryField.order is not None:
            return self.TableQueryField.order
        elif self.FieldRole.order is not None:
            return self.FieldRole.order
        elif self.Field.order is not None:
            return self.Field.order
        else:
            # end of row, order alphabetically
            return 10000

    def set_fk_field(self, fk_field = None):
        # if field instance exists it will be passed in,
        # otherwise we create one and return it
        if not fk_field:
            fk_to = self.Field.foreign_key_table_object_id
            if fk_to:
                if self.Field.foreign_key_display:
                    criteria = {'id': self.Field.foreign_key_display}
                else:
                    criteria = {'display_name': 'name'}

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
        if fk_field:
            self.FK_Field = fk_field.Field
            self.FK_FieldRole = fk_field.FieldRole
            self.FK_TableObject = fk_field.TableObject
        else:
            self.is_foreign_key = False # maybe no role access

    def set_dynamic_field(self, field_definition_id):
        oac = g_helper.get_org_access_control()
        dyn_data = oac.dynamic_field_data(self.Field.dynamic_field_definition_field_id, field_definition_id)

        for field, value in dyn_data:
            if hasattr(self.Field, field):
                setattr(self.Field, field, value)

    def _get_type(self):
        return self.DataType.name.lower()

    def _get_calculation_fields(self, calculation):
        calc_fields = {}
        if calculation:
            res = self.rac.calculation_fields(
                    calculation.id
            )
            for row in res:
                name = row.TableObject.name + '|' + row.Field.display_name
                calc_fields[name] = row
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
                    (self.Field.display_name == 'name' and not self.is_foreign_key) or
                    self.is_title_field or
                    (
                        self.is_foreign_key and
                        # since we're storing fk data once per field we don't have
                        # data on both name and fk_display for same table from
                        # oac query, this is rare and acceptable
                        self.FK_Field.display_name == 'name' and
                        self.FK_TableObject.name != 'long_text' and
                        self.visible
                    )
                )
            )

    def get_link(self, url_root, page = None, table = None):
        link = url_root + g.facility + '/' + 'core'
        if page:
            link += '/' + page
        if table:
            link += '/' + table + '/'
        return link

    def get_file_link(self, url_root, row_name, file):
        link = (url_root + g.facility
                + '/core/files/' + self.TableObject.name + '/'
                + row_name + '/' + file)
        return link
