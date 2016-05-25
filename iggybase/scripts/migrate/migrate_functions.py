''' enter functions here for custom value migrations

    there are some generic functions available
    below that add your own
'''

''' helper functions start '''
max_id = None

def get_col_name(col, col_name_map):
    if col in col_name_map:
        return col_name_map[col]
    return col
''' helper functions end '''

''' general functions start '''
def split_name(col, val, col_name_map):
    if '_' in val:
        names = val.split('_', 1)
        first, last = names[0], names[1]
    else:
        first = val
        last = ''
    new_dict = {'first_name': first, 'last_name': last}
    return new_dict

def get_fk(col, val, col_name_map):
    new_dict = {}
    if col in config.fk_tbl_map:
        new_col = config.fk_tbl_map[col]
    else:
        new_col = col
    fk_id = pk_exists(val, 'name', new_col)
    if fk_id:
        if col in col_name_map:
            new_dict = {col_name_map[col]: fk_id}
        else:
            new_dict = {(new_col + '_id'): fk_id}
    return new_dict

def make_numeric(col, val, col_name_map):
    new_dict = {}
    arr = re.split('[^0-9]', val)
    number = arr[0]
    if number == '':
        number = 'NULL'
    else:
        new_dict = {get_col_name(col, col_name_map):number}
    return new_dict

def get_active(col, val, col_name_map):
    new_dict = {}
    col_name = get_col_name(col, col_name_map)
    if val == 'ACTIVE':
        new_dict = {col_name:1}
    else:
        new_dict = {col_name:0}
    return new_dict

def get_bool(col, val, col_name_map):
    new_dict = {}
    val.strip()
    col_name = get_col_name(col, col_name_map)
    if val == 'yes' or val == 'Y' or val == 'y':
        new_dict = {col_name:1}
    else:
        new_dict = {col_name:0}
    return new_dict
''' general functions end '''

''' custom functions start, til EOF '''
def get_status(col, val, col_name_map):
    new_dict = {}
    if fk_tbl_map[col]:
        new_tbl = fk_tbl_map[col]
        fk_id = pk_exists(val, 'name', new_tbl)
        if fk_id:
            new_dict = {(new_tbl + '_id'): fk_id}
    return new_dict

def insert_long_text(col, val, col_name_map):
    global to_db
    global max_id
    if col == 'notes':
        col_name = 'note_id'
    else:
        col_name = col
    # check if the long_text exists
    sql = 'select id from long_text where long_text = "' + val.replace('"','') + '"'
    long_text = to_db.cursor()
    long_text.execute(sql)
    long_text = long_text.fetchone()
    if long_text and long_text[0]:
        return {col_name: long_text[0]}
    if not max_id:
        sql = 'select max(id) from long_text'
        max_id = to_db.cursor()
        max_id.execute(sql)
        max_id = max_id.fetchone()
        if max_id:
            max_id = max_id[0]
    if not max_id:
        max_id = 1
    else:
        max_id = max_id + 1
    # TODO: we need to fix name to not have constant 4 zeros
    if len(str(max_id)) == 1:
        name = 'LT00000' + str(max_id)
    else:
        name = 'LT0000' + str(max_id)
    sql = (
        'insert into long_text (name, active, organization_id, long_text)'
        + ' values("' + name + '", 1, 8, "' + val.replace('"','') + '")'
    )
    try:
        print("\t\t\t" + sql)
    except:
        print("\t\t\t" + 'sql has bad chars')
    note = to_db.cursor()
    note.execute(sql)
    to_db.commit()
    fk_id = note.lastrowid
    new_dict = {col_name: fk_id}
    return new_dict

def get_fk_billable(col, val, col_name_map):
    if 'SUB' in val:
        new_col = 'submission'
    elif 'REA' in val:
        new_col = 'reagent_request'
    else:
        new_col = 'reagent_request'
    fk_id = pk_exists(val, 'name', new_col)
    if fk_id:
        if 'SUB' in val:
            new_dict = {'submission_id': fk_id}
        elif 'REA' in val:
            new_dict = {'reagent_request_id': fk_id}
        else:
            new_dict = {}
    return new_dict

def get_fk_user(col, val, col_name_map):

    if new_col == 'user':
        val = val.replace(' ','_')
    fk_id = pk_exists(val, 'name', new_col)
    if not fk_id and new_col == 'user':
        fk_id = pk_exists(val, 'email', new_col)

    if fk_id:
        if col in ['canceler','receiver','requester','orderer', 'pi',
        'owner_institution', 'operator']:
            new_dict = {col: fk_id}
        elif col in col_name_map:
            new_dict = {col_name_map[col]: fk_id}
        else:
            new_dict = {(new_col + '_id'): fk_id}
    return new_dict

def limit_val(col, val, col_name_map):
    val = val[0:50]
    new_dict = {get_col_name(col, col_name_map): val}
    return new_dict


