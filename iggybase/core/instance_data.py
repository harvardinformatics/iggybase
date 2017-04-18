from iggybase import g_helper
import logging

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
        if instance_name is not None and ('empty_row' == instance_name or 'new' == instance_name):
            self.new_instance = True
            self.instance.name = instance_name + '_' + str(index)
        elif instance_name is not None and ('empty_row' in instance_name or 'new' in instance_name):
            self.new_instance = True
            self.instance.name = instance_name
        elif self.instance.name is None or self.instance.name == '':
            self.instance.name = 'new_' + str(index)
            self.new_instance = True
        else:
            self.new_instance = False

    def set_name(self, instance_name):
        self.instance.name = instance_name

    def set_organization_id(self, row_org_id = None):
        oac = g_helper.get_org_access_control()

        if row_org_id is not None:
            if isinstance(row_org_id, int):
                self.instance.organization_id = row_org_id
            else:
                org_record = oac.get_row('organization', {'name': row_org_id})

                if org_record:
                    self.instance.organization_id = org_record.id

        if oac.current_org_id is not None:
            self.instance.organization_id = oac.current_org_id
        else:
            self.instance.organization_id = 1

    def set_foreign_key_field(self, table_id, field_object, value):
        oac = g_helper.get_org_access_control()

        try:
            value = int(value)
            fk_record = oac.get_row(field_object.FK_TableObject.name, {'id': value})
        except:
            if field_object.FK_TableObject.name == 'field':
                fk_record = oac.get_row(field_object.FK_TableObject.name, {field_object.FK_Field.display_name: value,
                                                                           'table_object_id': table_id})
            else:
                fk_record = oac.get_row(field_object.FK_TableObject.name, {field_object.FK_Field.display_name: value})

        if fk_record:
            setattr(self.instance, field_object.display_name, fk_record.id)
            return fk_record.id
        else:
            setattr(self.instance, field_object.display_name, None)
            return None
