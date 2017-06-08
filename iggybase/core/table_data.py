# from iggybase.core.field_collection import FieldCollection
from flask import abort
from iggybase import g_helper
from importlib import import_module
import logging


class TableData():
    def __init__(self, table_name):
        rac = g_helper.get_role_access_control()
        table_data = rac.has_access('TableObject', {'name': table_name})
        if table_data is None:
            logging.info('No ' + table_name + ' for you')
            logging.info('role id: ' + rac.role.name)
            abort(403)
        self.table_object = table_data.TableObject
        self.table_object_role = table_data.TableObjectRole

        self.table_instance = rac.get_table(table_name)

        if self.table_object.extends_table_object_id is None:
            self.extends = None
            self.extends_role = None
        else:
            table_data = rac.has_access('TableObject', {'id': self.table_object.extends_table_object_id})
            self.extends = table_data.TableObject
            self.extends_role = table_data.TableObjectRole

            self.extends_instance = rac.get_table(self.extends.name)

        self.level = 0
        self.parent_link_field_display_name = None
        self.parent = None
        self.link_data = None
        self.link_type = None

    @property
    def table_name(self):
        return self.table_object.name

    @property
    def table_id(self):
        return self.table_object.id

    @property
    def sqlalchemy_object_name(self):
        components = self.table_object.name.split('_')

        return "".join(x.title() for x in components)

    @property
    def table_display_name(self):
        if self.table_object is None:
            return None
        elif self.table_name == 'history':
            return self.table_name
        elif self.table_object_role and self.table_object_role.display_name is not None:
            return self.table_object_role.display_name
        elif self.table_object.display_name is not None:
            return self.table_object.display_name
        else:
            return self.table_name

    def initialize_fields(self):
        # if self.table_object is None:
        #     fields = FieldCollection()
        # elif self.table_object.name == 'history':
        #    fields = FieldCollection(None, self.table_object.name, {}, False)
        # else:
        #     fields = FieldCollection(None, self.table_object.name)

        # fields.set_fk_fields()
        # fields.set_defaults()

        # return fields
        pass

    def set_collection_data(self, level, parent, link_data, link_type, child_link_field):
        self.level = level
        self.parent = parent
        self.link_data = link_data
        self.link_type = link_type

        if level == 0:
            self.parent_link_field_display_name = None
        elif child_link_field is not None:
            self.parent_link_field_display_name = child_link_field
