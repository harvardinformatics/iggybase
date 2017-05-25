from iggybase.core.instance_data import InstanceData
from iggybase.core.constants import WorkflowStatus
import logging

def add_record(*args, **kwargs):
    instance_data = InstanceData(table_name=kwargs['table_name'], name='new')
    if 'fields' in kwargs:
        instance_data.set_values(kwargs['fields'])
    return instance_data.commit()

def update_record(*args, **kwargs):
    instance_data = InstanceData(table_name=kwargs['table_name'], name=kwargs['instance_name'])
    instance_data.set_values(kwargs['fields'])
    return instance_data.commit()

def initiate_billing(*args, **kwargs):
    return_values = {'status': False}
    instance_data = InstanceData(table_name='work_item_group', name='new')
    instance_data.set_values({'workflow_id': kwargs['workflow_id'],
                              'status': WorkflowStatus.IN_PROGRESS,
                              'step_id': kwargs['step_id']})

    commit_status, results = instance_data.commit()

    if not commit_status:
        logging.info('return after add work_item_group')
        return return_values.update(results)

    (work_item_group_id, work_item_group_data), = results.items()

    return_values['work_item_group_id'] = work_item_group_id
    return_values['work_item_group_name'] = work_item_group_data['name']

    instance_data = InstanceData(table_name='order', name='new', save=True)

    commit_status, results = instance_data.commit()

    if not commit_status:
        logging.info('return after add order')
        return return_values.update(results)

    logging.info('initiate_billing order results:')
    logging.info(results)
    (order_id, order_data), = results.items()

    return_values['order_id'] = order_id

    order_table_id = instance_data.table_data.id
    commit_status, results = add_record(table_name='work_item',
                                        fields={'work_item_group_id': work_item_group_id,
                                                'table_object_id': order_table_id,
                                                'row_id': order_id})

    if not commit_status:
        logging.info('return after add work_item')
        return return_values.update(results)

    return_values['status'] = commit_status

    return return_values
