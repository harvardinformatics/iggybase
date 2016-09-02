from config import Config

# db connection information
from_db = {
    'user':Config.MYSQL_MPM_USER,
    'password':Config.MYSQL_MPM_PASSWORD,
    'host':'localhost',
    'database':'bauer_minilims'
}

# name of the semantic columns
semantic_col_map = {
        'col_name':2,
        'value':3
}

# fk field to table
fk_tbl_map = {
        'group_member': 'user',
        'group': 'organization',
        'operator':'user',
        'sample_name':'sample',
        'status': 'status',
        'plasmid': 'plasmid',
        'strain':'strain',
        'oligo':'oligo',
        'requester':'user',
        'orderer':'user',
        'receiver':'user',
        'canceler':'user',
        'pi':'user',
        'owner_institution':'institution',
        'submitter_name':'user',
        'investigatorname':'user',
        'investigator_name':'user',
        'experiment_name':'submission',
        'experimentname':'submission',
        'lab_admin_name':'user'
}
func_params = {
        'get_price_item': ['organization_id'],
        'get_fk_billable': ['organization_id', 'billable_item_type'],
        'price_per_unit': ['quantity'],
        'insert_charge_method': ['charge_type']
}
keys_to_delete = {
        'submission':[
            'charge_type'
        ],
        'reagent_request':[
            'charge_type'
        ],
        'line_item': [
            'billable_item_type'
        ]
}

