from iggybase import utilities as util


class InstanceData():
    def __init__(self, instance, instance_name, index=0, parent_id=None):
        self.instance = instance
        self.parent_id = parent_id
        self.save = False
        self.table_name = instance.__tablename__
        self.old_name = None
        self.instance_name = None
        self.new_instance = None

        self.set_name(instance_name, index)

    def set_name(self, instance_name, index=0):
        if instance_name == 'empty_row':
            self.new_instance = True
            self.instance.name = 'empty_row_' + str(index)
        elif self.instance.name is None or self.instance.name == '' or instance_name == 'new':
            self.instance.name = 'new_' + str(index)
            self.new_instance = True
        else:
            self.new_instance = False

        self.old_name = self.instance.name
        self.instance_name = self.instance.name

    def set_new_name(self, table_object=None):
        if table_object is None:
            table_object = util.get_table(self.table_name)

        self.instance_name = table_object.get_new_name()

        return self.instance_name
