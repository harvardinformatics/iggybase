#from iggybase import g_helper
#from iggybase import utilities as util

def insert_line_item(test):
    '''oac = g_helper.get_org_access_control()
    sample_no = test.number_of_samples
    hours = test.billable_hours
    analysis_id = test.analysis_id
    criteria = {
            'sample': {
                'id':test.sample_id,
            }
    }
    first_row = True
    order_info = oac.get_row_multi_tbl(['sample', 'line_item', 'order'], criteria, [], first_row)
    cols = {
            'organization_id': oac.current_org_id,
            'order_id': order_info.Order.id,
            'active': 1
    }
    if sample_no:
        price = find_price(analysis_id, sample_no, 'sample')
        per_sam = {
            'quantity': sample_no,
            'price_item_id': price.PriceItem.id,
            'price_per_unit': price.PriceList.price_per_unit
        }
        per_sam.update(cols)
        line_item = oac.insert_row('line_item', per_sam)
    if hours:
        price = find_price(analysis_id, hours, 'hour')
        per_hour = {
            'quantity': hours,
            'price_item_id': price.PriceItem.id,
            'price_per_unit': price.PriceList.price_per_unit
        }
        per_hour.update(cols)
        line_item = oac.insert_row('line_item', per_hour)'''
    line_item = None
    return line_item

def find_price(analysis_id, quantity, unit_type):
    '''oac = g_helper.get_org_access_control()
    analysis_to = oac.get_row('table_object', {'name': 'analysis'})
    unit = oac.get_row('unit', {'name': unit_type})
    org_row = oac.get_row('organization', {'id': oac.current_org_id})
    org_type_id = getattr(org_row, 'organization_type_id')
    criteria = {
            'price_item': {
                'unit_id': unit.id
            },
            'price_item_assoc': {
                'table_object_id':analysis_to.id,
                'row_id': analysis_id
            },
            'price_list': {
                'organization_type_id': org_type_id,
                'minimum_quantity': {'compare': 'less than equal', 'value': quantity}
            }
    }

    order_by = oac.format_order_by({'minimum_quantity':{'desc':True}})
    first_row = True
    price = oac.get_row_multi_tbl(['price_item', 'price_item_assoc',
    'price_list'], criteria, order_by, first_row)'''
    price = None
    return price
