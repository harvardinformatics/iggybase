class InstanceData():
    def __init__(self, instance, instance_name, index=0, parent_id=None):
        self.instance = instance
        self.parent_id = parent_id
        self.save = False
        self.new_instance = None
        self.form_index = index

        self.initialize_name(instance_name, index)

        self.old_name = self.instance.name

    @property
    def table_name(self):
        return self.instance.__tablename__

    @property
    def instance_class(self):
        return self.instance.__class__

    @property
    def instance_name(self):
        return self.instance.name

    def initialize_name(self, instance_name, index=0):
        if instance_name == 'empty_row':
            self.new_instance = True
            self.instance.name = 'empty_row_' + str(index)
        elif self.instance.name is None or self.instance.name == '' or instance_name == 'new':
            self.instance.name = 'new_' + str(index)
            self.new_instance = True
        else:
            self.new_instance = False

    def set_name(self, instance_name):
        self.instance.name = instance_name
