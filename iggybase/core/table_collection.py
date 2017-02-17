from iggybase.core.field_collection import FieldCollection
from collections import OrderedDict
from iggybase import g_helper
from flask import abort
from iggybase import utilities as util
import logging


class TableCollection():
    def __init__(self, table_name, depth = 2):
        self.role_access_control = g_helper.get_role_access_control()
        self.organization_access_control = g_helper.get_org_access_control()

        self.table_name = table_name
        self.table_names = OrderedDict()
        self.table_object = OrderedDict()
        self.extends = {}
        self.extends_role = {}
        self.table_object_role = {}
        self.table_meta_data = OrderedDict()
        self.level = {}
        self.link_display_name = {}
        self.parent = {}
        self.link_data = {}
        self.link_type = {}
        self.fields = {}

        self.get_tables(depth)

        if self.table_meta_data[table_name] is None:
            abort(403)

    def get_display_name(self, table_name):
        if table_name == 'history':
            return table_name
        elif self.table_object_role[table_name].display_name is not None:
            display_name = self.table_object_role[table_name].display_name
        elif self.table_meta_data[table_name].display_name is not None:
            display_name = self.table_meta_data[table_name].display_name
        else:
            display_name = table_name

        return display_name

    def get_tables(self, depth=2):
        access = self.role_access_control.has_access('TableObject',{'name': self.table_name})
        if access.TableObject.extends_table_object_id:
            extends = self.role_access_control.has_access('TableObject',{'id':
                                                                         access.TableObject.extends_table_object_id})
            self.initialize_table(access.TableObject, access.TableObjectRole, extends.TableObject,
                                  extends.TableObjectRole)
        else:
            self.initialize_table(access.TableObject, access.TableObjectRole)

        history = self.organization_access_control.get_table_object({'name': 'history'})
        self.initialize_table(history)

        if depth > 0 and self.table_meta_data[self.table_name]:
            data = self.role_access_control.get_link_tables(self.table_meta_data[self.table_name], depth)

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
        self.table_object[table_object.name] = util.get_table(table_object.name)

        self.table_meta_data[table_object.name] = table_object
        self.table_object_role[table_object.name] = table_object_role
        self.extends[table_object.name] = table_extends
        self.extends_role[table_object.name] = table_extends_role

        self.table_names[table_object.name] = self.get_display_name(table_object.name)

        self.level[table_object.name] = level
        self.parent[table_object.name] = parent
        self.link_data[table_object.name] = link_data
        self.link_type[table_object.name] = link_type

        self.initialize_fields(table_object.name)

        if level == 0:
            self.link_display_name[table_object.name] = None
        else:
            self.link_display_name[table_object.name] = (self.fields[table_object.name].fields_by_id[(table_object.id,
                                                         link_data.child_link_field_id)].Field.display_name)

    def initialize_fields(self, table_name):
        if table_name == 'history':
            self.fields[table_name] = FieldCollection(None, table_name, {}, False)
        else:
            self.fields[table_name] = FieldCollection(None, table_name)
        self.fields[table_name].set_fk_fields()
