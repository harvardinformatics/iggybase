from iggybase.core.table_data import TableData
from collections import OrderedDict
from iggybase import g_helper
from flask import abort
import logging


class TableCollection():
    def __init__(self, table_names = [], depth = 2):
        self.role_access_control = g_helper.get_role_access_control()
        self.organization_access_control = g_helper.get_org_access_control()

        self.depth = depth
        self.table_names = []
        self.tables = OrderedDict()
        self.get_tables(table_names)

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

    def get_tables(self, table_names):
        for table_name in table_names:
            self.add_table(table_name)

    def add_table(self, table_name):
        if 'history' not in self.table_names:
            history = self.organization_access_control.get_table_object({'name': 'history'})
            self.initialize_table(history)

        access = self.role_access_control.has_access('TableObject',{'name': table_name})
        if access.TableObject.extends_table_object_id:
            extends = self.role_access_control.has_access('TableObject',{'id':
                                                                         access.TableObject.extends_table_object_id})
            self.initialize_table(access.TableObject, access.TableObjectRole, extends.TableObject,
                                  extends.TableObjectRole)
        else:
            self.initialize_table(access.TableObject, access.TableObjectRole)

        if self.depth > 0 and self.tables[table_name].table_object:
            data = self.role_access_control.get_link_tables(self.tables[table_name].table_object, self.depth)

            for index, link_data in enumerate(data):
                if link_data['table_meta_data']:
                    table_name = link_data['table_meta_data'].name
                    self.table_names.append(table_name)
                    self.tables[table_name] = TableData(table_name)

                    self.tables[table_name].initialize_table(link_data['level'],
                                          link_data['parent'],
                                          link_data['link_data'],
                                          link_data['link_type'])
