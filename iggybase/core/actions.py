from iggybase.core.instance_collection import InstanceCollection
from iggybase.core.constants import status
import logging

def add_record(*args, **kwargs):
    instance_collection = InstanceCollection(0, {kwargs['table_name']: ['new']})
    instance_collection.set_values(instance_collection.instance.instance_name, kwargs['fields'])
    return instance_collection.commit()

def update_record(*args, **kwargs):
    instance_collection = InstanceCollection(0, {kwargs['table_name']: [kwargs['instance_name']]})
    instance_collection.set_values(instance_collection.instance.instance_name, kwargs['fields'])
    return instance_collection.commit()

def initiate_smms_billing(*args, **kwargs):
    instance_collection = InstanceCollection(0, {'work_item_group': ['new']})
    instance_collection.set_values(instance_collection.instance.instance_name, {'workflow_id': kwargs['workflow_id'],
                                                                                'status': status.IN_PROGRESS,
                                                                                'step_id': kwargs['step_id'],
                                                                                'before_action_complete': 0})
    commit_status, results = instance_collection.commit()

    if not commit_status:
        return results

    instance_collection = InstanceCollection(0, {'order': ['new']})
    order_table_id = instance_collection.tables['order'].table_object.id
    instance_collection.set_values(instance_collection.instance.instance_name, {'workflow_id': kwargs['submitter_id'],
                                                                                'status': status.IN_PROGRESS,
                                                                                'step_id': kwargs['step_id'],
                                                                                'before_action_complete': 0})
    commit_status, tmp_results = instance_collection.commit()
    results.update(tmp_results)

    if not commit_status:
        return results

    work_item_group_id = results.keys()[0]

    instance_collection = InstanceCollection(0, {'work_item': ['new']})

    instance_collection.set_values(instance_collection.instance.instance_name, {'work_item_group_id': results.keys()[0],
                                                                                'status': status.IN_PROGRESS,
                                                                                'step_id': kwargs['step_id'],
                                                                                'before_action_complete': 0})

