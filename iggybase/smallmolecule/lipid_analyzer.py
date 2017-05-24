import csv
import os
from flask import current_app

def save_lipid_results(paths, ret_time_fil, group_pq_fil, group_sn_fil, group_area_fil,
    group_height_fil):
    selected = {}
    for path in paths:
        if path:
            with open(path,'r') as f:
                cols = []
                for i,ln in enumerate(f):
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
    selected_rows = [cols] + list(selected.values())
    result_path = current_app.root_path + 'files/lipid_analysis/'
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    with open(result_path + 'lipid_analysis.csv','w') as c:
        writer = csv.writer(c)
        writer.writerows(selected_rows)
    return True

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
