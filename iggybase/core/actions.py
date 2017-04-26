from iggybase.core.instance_collection import InstanceCollection
from iggybase.core.constants import WorkflowStatus
import logging

def add_record(*args, **kwargs):
    instance_collection = InstanceCollection(0, {kwargs['table_name']: ['new']})
    if 'fields' in kwargs:
        instance_collection.set_values(instance_collection.instance.instance_name, kwargs['fields'])
    return instance_collection.commit()

def update_record(*args, **kwargs):
    instance_collection = InstanceCollection(0, {kwargs['table_name']: [kwargs['instance_name']]})
    instance_collection.set_values(instance_collection.instance.instance_name, kwargs['fields'])
    return instance_collection.commit()

def initiate_smms_billing(*args, **kwargs):
    logging.info('initiate_smms_billing')
    instance_collection = InstanceCollection(0, {'work_item_group': ['new']})
    instance_collection.set_values(instance_collection.instance.instance_name, {'workflow_id': kwargs['workflow_id'],
                                                                                'status': WorkflowStatus.IN_PROGRESS,
                                                                                'step_id': kwargs['step_id'],
                                                                                'before_action_complete': 0})

    commit_status, results = instance_collection.commit()

    if not commit_status:
        return commit_status, results

    (work_item_group_id, work_item_group_data), = results.items()

    commit_status, tmp_results = add_record(table_name='order')

    if not commit_status:
        return commit_status, tmp_results

    (order_id, order_data), = results.items()
    order_table_id = instance_collection.tables['order'].table_object.id
    commit_status, tmp_results = add_record(table_name='work_item_group',
                                            instance_name=work_item_group_data['name'],
                                            fields={'workflow_item_group_id': work_item_group_id,
                                                    'table_object_id': order_table_id,
                                                    'row_id': order_id})

    if not commit_status:
        return commit_status, tmp_results

    results.update(tmp_results)

    return commit_status, results
