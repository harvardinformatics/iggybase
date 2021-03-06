from config import Config

db = {
    'user':Config.DB_USER,
    'password':Config.DB_PASSWORD,
    'host': Config.DB_HOST,
    'database': Config.DATA_DB_NAME

}

# name of the semantic columns
semantic_col_map = {
        'col_name':3,
        'value':4
}

# col name old to new, base map used for all tables
base_col_name_map = {
    'date_modified': 'last_modified',
    'deleted': 'active',
    'submitter_name':'submitter',
    'expense_code_1':'expense_code',
    'sample_name':'sample_id',
    'investigatorname':'investigator',
    'investigator_name':'investigator',
    'lab_admin_name':'lab_admin'

}
# col name old to new, by table
col_name_map = {
    'submission': {
        'submitter': 'user'
        },
    'invoice': {
        'group': 'invoice_organization',
        'total_cost': 'amount',
        'month': 'invoice_month',
        'status':'status_id',
        'notes': 'note_id'
        },
    'line_item':{
        'cost': 'price_per_unit',
        'sequencing_price': 'price_item_id',
        'billable_item': 'price_item_id'
    },
    'sample_sheet':{
        'adapter':'adapter_1',
        'adapterread2':'adapter_2',
        'iemfileversion':'iemfile_version'
        },
    'sample':{
        'fragment_size_(bp)':'fragment_size',
        'multiplex_sample_-_lane_id':'multiplex_sample_lane_id',
        },
    'sequencing_price':{
        'single_lane/full_flowcell':'lane_type',
        },
    'group_member':{
        'group': 'oganization_id'
    },
    'oligo_batch':{
        'receiver_date': 'receive_date'
    },
    'reagent_request':{
        'submitter': 'user',
        'note_id': 'comments',
        'notes': 'comments'
    }
}

# col value assignments or function, base used for all tables
base_col_value_map = {
    'organization_id': 1,
    'active': 1
}

# col value addignments or function, by table
col_value_map = {
    'table_object':{
        'module_id':10,
        'id_length': 6,
        'admin_table':0,
        'new_name_id':1
        },
    'field_role':{
        'visible':1
        },
    'invoice':{
        'line_item':None,
        'lab_admin_name':None,
        'lab_admin_email':None,
        'group': 'func_get_fk',
        'invoice_number': None,
        'notes': 'func_insert_long_text',
        'status': 11,
        'total_credit': None
        },
    '''invoice':{
        'line_item':'func_get_fk',
        'lab_admin_name':'func_get_fk_user',
        'lab_admin_email':None
        },'''
    'line_item':{
        'invoice_type':None,
        'group':'func_get_fk',
        'lab_admin_name': None,
        'lab_admin': None,
        'expense_code_percentage': None,
        'billable_item': 'func_get_fk_billable',
        #'billable_item': None,
        #'billable_item_type': 'func_get_reagent_price_item',
        'lab_admin_email': None,
        'expense_code': None,
        'delivery_date': None,
        'month': None,
        'group_member': None,
        'status_id': 5,
        'purchase_order': None,
        'reagent': None,
        'status': None,
        'quantity':'func_make_numeric',
        'sequencing_price':'func_get_price_item',
        #'reagent_request':'func_get_reagent_price_item',
        'cost':'func_price_per_unit'
        },
    'illumina_flowcell':{
        'illumina_run':'func_get_fk',
        'directory_location':None,
        'directory_size':None,
        'notes':None,
        'read_length':None,
        'library_type':None
        },
    'sample_sheet':{
        'illumina_flowcell':'func_get_fk',
        'illumina_run':'func_get_fk',
        'machine':'func_get_fk',
        'experiment_name':'func_get_fk',
        'experimentname':'func_get_fk',
        'investigatorname':'func_get_fk_user',
        'investigator_name':'func_get_fk_user',
        },
    'illumina_run':{
        'submission':'func_get_fk',
        'machine':'func_get_fk',
        'illumina_bclconversion_analysis':'func_get_fk',
        'read_1_index':'func_get_bool',
        'read_2_index':'func_get_bool',
        'read_3_index':'func_get_bool',
        'read_4_index':'func_get_bool',
        'illumina_flowcell':None,
        'count':None,
        'bustardsummary.xml':None,
        'runname':None,
        'yield':None,
        'clusters':None,
        'passing_clusters':None,
        'passing_clusters_percent':None,
        'kb_sequenced':None,
        'call_cycle':None,
        'image_cycle':None,
        'num_cycles':None,
        'percent_called':None,
        'percent_imaged':None,
        'percent_scored':None,
        'run_started':None,
        'score_cycle':None,
        'demultiplex_stats.htm':None,
        'ivc_html':None,
        'all_html':None,
        'notes':None,
        'run_sample_sheet':None
        },
    'illumina_bclconversion_analysis':{
        'illumina_run':None,
        'submission':'func_get_fk',
        'run_directory':None,
        'illumina_lane':None,
        'timestamp':None,
        'data_directory':None,
        'command':'func_insert_long_text'
        },
    'sample_sheet_item':{
        'operator':'func_get_fk_user',
        'project':'func_get_fk',
        'submission':'func_get_fk',
        'sample_name':'func_get_fk',
        'sample_sheet':'func_get_fk',
        'recipe':'func_make_numeric',
        'lane':'func_make_numeric',
        'control':'func_get_bool',
        'i5_index_id':None,
        'i7_index_id':None,
        'index2':None,
        'sample_id':None,
        'sample_project':None,
        'sample_plate':None,
        'sample_well':None,
        },
    'sample':{
        'bioanlyzer_performed':'func_get_bool',
        'qpcr_performed':'func_get_bool',
        'qubit_performed':'func_get_bool',
        'volume_(ul)':'func_make_numeric',
        'read_length':'func_make_numeric',
        'concentration':'func_make_numeric',
        'submission':'func_get_fk',
        'low_diversity_library':'func_get_bool',
        'is_dual_indexed':'func_get_bool',
        'project':'func_get_fk',
        'index_sequence':'func_insert_long_text',
        'bioanalyzer_service_requested':'func_get_bool',
        'date_finished':None,
        'date_received':None,
        'primer_type':None,
        'use_index':None,
        'bioanalyzer_status':None,
        'bioanalyzer_file':None,
        'notes':None
        },
    'submission': {
        'index_list': None,
        'submitter_name':'func_get_org_fk_user',
        'submitter':'func_get_org_fk_user',
        'comments':'func_insert_long_text',
        'purchase_order_file':None,
        'purchase_order_number':None,
        'destination_directory':None,
        'run_type':None,
        'expense_code_2':'func_insert_charge_method',
        'expense_code_3': 'func_insert_charge_method',
        'expense_code_4': 'func_insert_charge_method',
        'expense_code_1': 'func_insert_charge_method',
        'qpcr_service_requested': None,
        'phone':None,
        'email':None,
        'pi':None,
        'group': None,
        'status': None,
        'expense_code_percentage_1': None,
        'expense_code_percentage_2': None,
        'expense_code_percentage_3': None,
        'expense_code_percentage_4': None,
        'invoice_month': None,
        'illumina_run': None
        },
    'reagent_request':{
        'expense_code_2':'func_insert_charge_method',
        'expense_code_3': 'func_insert_charge_method',
        'expense_code_4': 'func_insert_charge_method',
        'expense_code_1': 'func_insert_charge_method',
        'submitter_name':'func_get_org_fk_user',
        'submitter':'func_get_org_fk_user',
        #'reagent':'func_get_fk',
        'reagent':None,
        'group': None,
        'purchase_order_number':None,
        'purchase_order_file':None,
        'notes':'func_insert_long_text',
        #'quantity':'func_make_numeric',
        'quantity':None,
        'expense_code_percentage_1': None,
        'expense_code_percentage_2': None,
        'expense_code_percentage_3': None,
        'expense_code_percentage_4': None,
        'status': None,
        'invoice_month': None
        },
    'purchase_order':{
        'status':'func_get_active',
        'pi':'func_get_fk_user',
        'owner':'func_get_fk_user',
        'owner_institution':'func_get_fk'
        #'billing_address':None,
        #'owner_address': None
        },
    'sequencing_price':{
        'paired_end':'func_get_bool'
        },
    'group':{
        'group_member': None,
        'group': None, #organization tbl exception
        'pi': None,
        'department': 'func_get_fk',
        'type': None,
        'lab_admin': None,
        'sequencing_notes': None,
        'web_page': None,
        'location': None
    },
    'group_member':{
        'full_name': 'func_split_name',
        'admin': None,
        'phone': None,
        'street_address': None,
        'city': None,
        'state': None,
        'zip': None,
        'institution': None,
        'affiliation':None,
        'picture': None,
        'notes':None,
        'state': None,
        'institution_type': None,
        'user_id': None,
        'postal_code': None,
        'title': None,
        'department': None,
        'comments': None,
        'rc_login_id': None,
        'spinal_expense_code': None
    },
    'user':{
        'full_name': None,
        'admin': None,
        'phone': None,
        'street_address': None,
        'city': None,
        'state': None,
        'zip': None,
        'institution': None,
        'affiliation':None,
        'picture': None,
        'notes':None,
        'state': None,
        'institution_type': None,
        'user_id': None,
        'postal_code': None,
        'title': None,
        'department': None,
        'group': 'func_get_fk',
        'name': 'func_get_fk'
    },
    'oligo':{
        'sequence':'func_insert_long_text',
        'status':'func_get_fk'
    },
    'strain':{
        'background':'func_insert_long_text',
        'comments':'func_insert_long_text'
    },
    'plasmid':{
        'mod_notes':'func_insert_long_text',
        'constr_notes':'func_insert_long_text',
        'insert_notes':'func_insert_long_text',
        'vector_notes':'func_insert_long_text',
        'publications':'func_insert_long_text',
        'purpose':'func_insert_long_text'
    },
    'fragment':{
        'plasmid':'func_get_fk',
        'description':'func_insert_long_text'
    },
    'genotype':{
        'strain':'func_get_fk',
        'genotype_id':None
    },
    'oligo_fragment':{
        'oligo':'func_get_fk',
        'description':'func_insert_long_text'
    },
    'oligo_batch':{
        'oligo':'func_get_fk',
        'orderer':'func_get_fk_user',
        'receiver':'func_get_fk_user',
        'requester':'func_get_fk_user',
        'canceler':'func_get_fk_user',
        'order_notes':'func_insert_long_text',
        'cancel_notes':'func_insert_long_text',
        'request_notes':'func_insert_long_text',
        'oligo_batch_id': None,
    }
}
# adds columns to the table
base_add_cols_map = {
        'active': 1,
        #'organization_id':84
}
# by table
add_cols_map = {
        'organization':{
            'organization_id':1,
            'parent_id':1040
        },
        'user_organization':{
            #'func_user_org':'func_user_org'
            'organization_id':1,
            'default_organization': 1
        }
}

# int cols
base_int_col_map = ['id', 'active', 'organization_id', 'note_id', 'user_id',
'department_id', 'machine_id', 'project_id', 'role_id', 'table_object_id',
'illumina_bclconversion_analysis_id','illumina_run_id','illumina_flowcell_id',
'sample_sheet_id', 'reagent_request_id', 'sequencing_price_id', 'order',
'field_id', 'status_id', 'passed', 'billable', 'row_id', 'line_item_id',
'module_id', 'id_length', 'admin_table', 'price_item_id', 'order_id',
'address_id', 'billing_address_id', 'institution_id', 'department_id',
'parent_id']
# by table
int_col_map = {
        'invoice': [
            'invoice_organization_id',
            'notes'
        ],
        'user_organization_position': [
            'position_id',
            'user_organization_id'
        ],
        'charge_method': [
            'charge_method_type_id'
        ],
        'order_charge_method':[
            'charge_method_id',
            'percent'
            ],
        'user_organization':[
            'default_organization',
            'user_organization_id',
            'user_id'
            ],
        'field':[
            'length',
            'data_type_id',
            'unique',
            'primary_key',
            'foreign_key_table_object_id',
            'foreign_key_field_id',
            ],
        'read':[
            'indexed',
            'cycles'
        ],
        'line_item':[
            'price_per_unit',
            'quantity',
            'invoice_id'
        ],
        'field_role':[
            'visible',
            ],
        'table_object':[
            'module_id',
            'id_length',
            'admin_table',
            'new_name_id',
            ],
        'illumina_run':[
            'machine_id',
            'read_1_cycles',
            'read_2_cycles',
            'read_3_cycles',
            'read_4_cycles',
            'read_1_index',
            'read_2_index',
            'read_3_index',
            'read_4_index'
            ],
        'illumina_bclconversion_analysis':[
            'job_id',
            'command'
            ],
        'illumina_flowcell':[
            'illumina_run_id',
            'lane_count',
            'swath_count',
            'surface_count',
            'tile_count'
        ],
        'sample_sheet':[
            'read_length_1'
        ],
        'sample_sheet_item':[
            'control',
            'operator',
            'lane_id',
            'recipe',
            'order_id',
            'sample_sheet_id'
            ],
        'lane':[
            'lane_number'
        ],
        'sample':[
            'read_length',
            'bioanlyzer_performed',
            'qpcr_performed',
            'qubit_performed',
            'volume',
            'concentration',
            'low_diversity_library',
            'is_dual_indexed',
            'index_sequence',
            'bioanalyzer_service_requested',
            'project_id',
            'submission_id'
            ],
        'order':[
            'submitter_id',
            'comments'
            ],
        'illumina_adapter':[
            'number'
            ],
        'reagent':[
            'status',
            'price_per_unit',
            'reagent_active'
            ],
        'purchase_order':[
            'total_amount',
            'remaining_amount',
            'po_active',
            'pi'
            ],
        'sequencing_price':[
            'harvard_code_price',
            'paired_end',
            'read_length',
            'po_price',
            'commercial_price',
            'outside_academic_price'
            ],
        'oligo': [
            'sequence', 'status'
        ],
        'strain': [
            'background', 'comments'
        ],
        'plasmid': [
            'mod_notes', 'constr_notes', 'insert_notes', 'vector_notes',
            'publications', 'purpose'
        ],
        'fragment': [
            'plasmid_id', 'description'
        ],
        'genotype': [
            'strain_id'
        ],
        'oligo_fragment':[
            'oligo_id', 'description'
        ],
        'oligo_order':[
            'oligo_id', 'orderer',
            'receiver','canceler','order_notes','cancel_notes',
            'requester','request_notes'
        ],
        'table_object':[
                'new_name_id'
        ]
}

# date cols
base_date_col_map = ['last_modified', 'date_created', 'entry_date',
'valid_from_date', 'invoice_month', 'run_date', 'start_date', 'end_date']
# by table
date_col_map = {
    'oligo_order': [
        'request_date','order_date','cancel_date','receive_date'
    ],
    'invoice':[
        'month'
        ],
    'line_item':[
        'month',
        'delivery_date'
        ],
    'sample_sheet':[
        'date'
        ],
    'illumina_run':[
        'run_date'
        ],
    'illumina_bclconversion_analysis':['launch_timestamp'],
    'reagent_request':[
        'invoice_month'
        ]
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

# use to just skip some troublesome rows
keys_to_skip = ['Weinstein_Bryan', 'Bryan Weinstein', 'Bryan_Weinstein',
        'Testy_McTesterson', 'Lester_Kobzik',
        'David_Doupe2','Kathy_LoBuglio','2150030660','0007281637', 'Admin',
        'Guest', 'Bioteam']
