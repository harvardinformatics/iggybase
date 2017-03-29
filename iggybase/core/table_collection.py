from iggybase.core.field_collection import FieldCollection
from iggybase.core.table_data import TableData
from collections import OrderedDict
from iggybase import g_helper
from flask import abort
import logging


class TableCollection():
    def __init__(self, table_names = [], depth = 2):
        self.role_access_control = g_helper.get_role_access_control()
        self.organization_access_control = g_helper.get_org_access_control()

        self.table_names = []
        self.tables = OrderedDict()

        self.get_tables(table_names, depth)

    def __iter__(self):
        return iter(self.tables)

    def __getitem__(self, table_name):
        return self.tables[table_name]

    def keys(self):
        return self.tables.keys()

    def items(self):
        return self.tables.items()

    def values(self):
        return self.tables.values()

    def get_tables(self, table_names, depth):
        history = self.organization_access_control.get_table_object({'name': 'history'})
        self.initialize_table(history)

        for table_name in table_names:
            access = self.role_access_control.has_access('TableObject',{'name': table_name})
            if access.TableObject.extends_table_object_id:
                extends = self.role_access_control.has_access('TableObject',{'id':
                                                                             access.TableObject.extends_table_object_id})
                self.initialize_table(access.TableObject, access.TableObjectRole, extends.TableObject,
                                      extends.TableObjectRole)
            else:
                self.initialize_table(access.TableObject, access.TableObjectRole)

            if depth > 0 and self.tables[table_name].table_object:
                data = self.role_access_control.get_link_tables(self.tables[table_name].table_object, depth)

                for index, link_data in enumerate(data):
                    if link_data['table_meta_data']:
                        self.initialize_table(link_data['table_meta_data'],
                                              link_data['table_role_data'],
                                              link_data['table_extends'],
                                              link_data['table_extends_role'],
                                              link_data['level'],
                                              link_data['parent'],
                                              link_data['link_data'],
                                              link_data['link_type'])

    def initialize_table(self, table_object, table_object_role=None, table_extends=None, table_extends_role=None,
                         level=0, parent=None, link_data=None, link_type=None):
        if table_object is None:
            abort(403)
        self.table_names.append(table_object.name)

        self.tables[table_object.name] = TableData(table_object, table_object_role)

        self.tables[table_object.name].extends = table_extends
        self.tables[table_object.name].extends_role = table_extends_role
        self.tables[table_object.name].level = level
        self.tables[table_object.name].parent = parent
        self.tables[table_object.name].link_data = link_data
        self.tables[table_object.name].link_type = link_type

        self.initialize_fields(table_object.name)

        if level == 0:
            self.tables[table_object.name].parent_link_field_display_name = None
        elif table_extends is None:
            self.tables[table_object.name].parent_link_field_display_name = \
                (self.tables[table_object.name].fields.fields_by_id[(table_object.id,
                                                              link_data.child_link_field_id)].Field.display_name)
        else:
            self.tables[table_object.name].parent_link_field_display_name = \
                (self.tables[table_object.name].fields.fields_by_id[(table_extends.id,
                                                              link_data.child_link_field_id)].Field.display_name)

    def initialize_fields(self, table_name):
        if table_name == 'history':
            self.tables[table_name].fields = FieldCollection(None, table_name, {}, False)
        else:
            self.tables[table_name].fields = FieldCollection(None, table_name)
        self.tables[table_name].fields.set_fk_fields()
