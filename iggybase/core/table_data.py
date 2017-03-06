from iggybase import utilities as util


class TableData():
    def __init__(self, table_object=None, table_object_role=None):
        self.table_object = table_object
        self.table_object_role = table_object_role

        if table_object is None:
            self.table_name = None
            self.table_instance = None
            self.table_display_name = None
        else:
            self.table_name = table_object.name
            self.table_instance = util.get_table(table_object.name)
            self.set_display_name()

        self.extends = None
        self.extends_role = None
        self.level = None
        self.parent_link_field_display_name = None
        self.parent = None
        self.link_data = None
        self.link_type = None
        self.fields = None

    def set_display_name(self):
        if self.table_name == 'history':
            self.table_display_name = self.table_name
        elif self.table_object_role and self.table_object_role.display_name is not None:
            self.table_display_name = self.table_object_role.display_name
        elif self.table_object.display_name is not None:
            self.table_display_name = self.table_object.display_name
        else:
            self.table_display_name = self.table_name
