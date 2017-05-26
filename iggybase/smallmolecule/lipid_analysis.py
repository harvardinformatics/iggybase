import csv
import os
from flask.ext import excel
from config import Config
from collections import OrderedDict

class LipidAnalysis:
    def __init__ (self, paths):
        self.paths = paths
        self.rows = self.get_rows_from_files(self.paths)

    def get_rows_from_files(self, paths):
        rows = OrderedDict()
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
                            row_d = OrderedDict(zip(cols, row))
                            ret_time = self.avg_col_type(row_d, 'GroupTopPos')
                            row_d['ret_time'] = ret_time
                            row_d.move_to_end('ret_time', last=False)
                            name = row_d['LipidIon'] + '_' + str(ret_time)
                            row_d['name'] = name
                            row_d.move_to_end('name', last=False)
                            rows[name] = row_d
        return rows

    def get_cols(self):
        first = list(self.rows.keys())[0]
        return list(self.rows[first].keys())

    def write_csv(self):
        result_path = Config.UPLOAD_FOLDER + '/lipid_analysis/'
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        with open(result_path + 'lipid_analysis.csv','w') as c:
            w = csv.DictWriter(c, self.get_cols())
            w.writeheader()
            w.writerows(self.rows.values())
            '''for row in self.rows.values():
                w.writerow(row.values())'''
        return True

    def subtract_blank(self, blank, mult_factor):
        if blank:
            subtracted = {}
            blank_cols = []
            area_cols = []
            area_start = 'Area['
            blank_start = area_start + blank
            for col in self.get_cols():
                if col.startswith(area_start):
                    if col.startswith(blank_start):
                        blank_cols.append(col)
                    else:
                        area_cols.append(col)
            for name, row in self.rows.items():
                avg_blank = self.calculate_avg_blank(blank_cols, row)
                include_row = False
                for col in area_cols:
                    normal = float(row[col]) - (avg_blank * mult_factor)
                    if normal < 0: # no neg areas
                        normal = 0
                    row[col] = normal
                    if normal > 0:
                        include_row = True
                if include_row:
                    row['normal'] = avg_blank
                    subtracted[name] = row
            self.rows = subtracted

    def calculate_avg_blank(self, blank_cols, row):
            avg_blank = 0
            for col in blank_cols:
                avg_blank += float(row[col])
            return avg_blank / len(blank_cols)

    def remove_columns(self, remove_cols):
        remove_cols = [x.strip().lower() for x in remove_cols.split(',')]
        clean_selected = {}
        removed_cols = []
        clean_cols = []
        for col in self.get_cols():
            prefix = col.split('[')[0]
            if prefix.lower() in remove_cols:
                removed_cols.append(col)
            else:
                clean_cols.append(col)
        for name, row in self.rows.items():
            new_row = OrderedDict()
            for col, val in row.items():
                if col not in removed_cols:
                    new_row[col] = val
            clean_selected[name] = new_row
        self.rows = clean_selected

    def avg_col_type(self, row, col_type):
        avg = 0
        cnt = 0.0
        for name, val in row.items():
            if col_type in name:
                avg += float(val)
                cnt += 1
        avg = avg/cnt
        return avg

    def filter_rows(self, ret_time_fil, group_pq_fil, group_sn_fil, group_area_fil,
            group_height_fil):
        selected = {}
        for name, row in self.rows.items():
            if self.filter_in(row, ret_time_fil, group_pq_fil, group_sn_fil,
                    group_area_fil, group_height_fil):
                selected[name] = row
        self.rows = selected

    def filter_in(self, row, ret_time_fil, group_pq_fil, group_sn_fil,
            group_area_fil, group_height_fil):
        if row['Rej.'] != '0':
            return False
        if row['ret_time'] <= ret_time_fil:
            return False
        group_pq_avg = self.avg_col_type(row, 'GroupPQ')
        if group_pq_avg <= group_pq_fil:
            return False
        group_sn_avg = self.avg_col_type(row, 'GroupS/N')
        if group_sn_avg <= group_sn_fil:
            return False
        if group_area_fil > 0: # all values are pos ints, so skip if 0
            group_area_avg = self.avg_col_type(row, 'GroupArea')
            if group_area_avg <= group_area_fil:
                return False
        if group_height_fil > 0: # all values are pos ints, so skip if 0
            group_height_avg = self.avg_col_type(row, 'GroupHeight')
            if group_height_avg <= group_height_fil:
                return False
        return True
