import csv
import os
from config import Config

def save_lipid_results(paths, ret_time_fil, group_pq_fil, group_sn_fil, group_area_fil,
    group_height_fil, blank, mult_factor, remove_cols):
    selected = {}
    for path in paths:
        if path:
            with open(path,'r') as f:
                for i,ln in enumerate(f):
                    if i == 0:
                        cols = []
                    if (ln.startswith('#') or ln.startswith('\t') or
                            ln.startswith('\n')):
                        continue
                    if not cols:
                        cols = ln.split('\t')
                    else: # data lines
                        row = ln.split('\t')
                        # remove trailing newline
                        row[(len(row) - 1)] = row[(len(row) - 1)].strip('\n')
                        ret_time = avg_col_type(row, 'GroupTopPos', cols)
                        if filter_rows(row, cols, ret_time, ret_time_fil,
                                group_pq_fil, group_sn_fil, group_area_fil,
                                group_height_fil):
                            lipid_ion = row[cols.index('LipidIon')]
                            name = lipid_ion + '_' + str(ret_time)
                            selected[name] = [name] + row
    cols = ['name'] + cols
    if blank:
        cols = cols + ['blank']
        selected = subtract_blank(selected, blank, cols, mult_factor)
    cols, selected = remove_columns(cols, selected, remove_cols)
    selected_rows = [cols] + list(selected.values())
    result_path = Config.UPLOAD_FOLDER + '/lipid_analysis/'
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    with open(result_path + 'lipid_analysis.csv','w') as c:
        writer = csv.writer(c)
        writer.writerows(selected_rows)
    return True

def subtract_blank(selected, blank, cols, mult_factor):
    normalized = {}
    blank_cols = []
    area_cols = []
    area_start = 'Area['
    blank_start = area_start + blank
    for i, col in enumerate(cols):
        if col.startswith(area_start):
            if col.startswith(blank_start):
                blank_cols.append(i)
            else:
                area_cols.append(i)
    for name, row in selected.items():
        avg_blank = calculate_avg_blank(blank_cols, row)
        include_row = False
        for i in area_cols:
            normal = float(selected[name][i]) - (avg_blank * mult_factor)
            if normal < 0: # no neg areas
                normal = 0
            row[i] = normal
            if normal > 0:
                include_row = True
        if include_row:
            print(avg_blank)
            normalized[name] = row + [avg_blank]
    return normalized

def calculate_avg_blank(blank_cols, row):
        avg_blank = 0
        for i in blank_cols:
            avg_blank += float(row[i])
        return avg_blank / len(blank_cols)

def remove_columns(cols, selected, remove_cols):
    remove_cols = [x.strip().lower() for x in remove_cols.split(',')]
    clean_cols = []
    clean_selected = {}
    removed_cols = []
    for i, col in enumerate(cols):
        prefix = col.split('[')[0]
        if prefix.lower() in remove_cols:
            removed_cols.append(i)
        else:
            clean_cols.append(col)
    for name, row in selected.items():
        clean_selected[name] = [item for j, item in enumerate(row) if j not in
                removed_cols]
    return clean_cols, clean_selected

def avg_col_type(row, col_type, cols):
    avg = 0
    cnt = 0.0
    for i, c in enumerate(cols):
        if col_type in c:
            avg += float(row[i])
            cnt += 1
    avg = avg/cnt
    return avg

def filter_rows(row, cols, ret_time, ret_time_fil, group_pq_fil, group_sn_fil,
        group_area_fil, group_height_fil):
    if row[cols.index('Rej.')] != '0':
        return False
    if ret_time <= ret_time_fil:
        return False
    group_pq_avg = avg_col_type(row, 'GroupPQ', cols)
    if group_pq_avg <= group_pq_fil:
        return False
    group_sn_avg = avg_col_type(row, 'GroupS/N', cols)
    if group_sn_avg <= group_sn_fil:
        return False
    if group_area_fil > 0: # all values are pos ints, so skip if 0
        group_area_avg = avg_col_type(row, 'GroupArea', cols)
        if group_area_avg <= group_area_fil:
            return False
    if group_height_fil > 0: # all values are pos ints, so skip if 0
        group_height_avg = avg_col_type(row, 'GroupHeight', cols)
        if group_height_avg <= group_height_fil:
            return False
    return True
