from iggybase.core.instance_collection import InstanceCollection
import logging

def add_record(self, table_name, fields):
    instance_collection = InstanceCollection(0, {table_name: ['new']})
    instance_collection.set_values(instance_collection.instance.instance_name, fields)
    return instance_collection.commit()

def update_record(self, table_name, instance_name, fields):
    instance_collection = InstanceCollection(0, {table_name: [instance_name]})
    instance_collection.set_values(instance_collection.instance.instance_name, fields)
    return instance_collection.commit()
