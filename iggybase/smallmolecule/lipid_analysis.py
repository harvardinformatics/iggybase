import csv
import os
import numpy
from flask.ext import excel
from config import Config
from collections import OrderedDict

class LipidAnalysis:
    def __init__ (self, paths):
        self.paths = paths
        self.rows = self.get_rows_from_files(self.paths)
        self.area_start = 'Area['

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

    def get_cols(self, start = None):
        first = list(self.rows.keys())[0]
        keys = list(self.rows[first].keys())
        if start:
            keys = [i for i in keys if i.startswith(start)]
        return keys

    def write_csv(self):
        success = False
        if self.rows:
            result_path = Config.UPLOAD_FOLDER + '/lipid_analysis/'
            if not os.path.exists(result_path):
                os.makedirs(result_path)
            with open(result_path + 'lipid_analysis.csv','w') as c:
                w = csv.DictWriter(c, self.get_cols())
                w.writeheader()
                w.writerows(self.rows.values())
                '''for row in self.rows.values():
                    w.writerow(row.values())'''
                success = True
        return success

    def subtract_blank(self, blank, mult_factor):
        if blank and self.rows:
            subtracted = {}
            area_cols = self.get_cols(self.area_start)
            blank_start = self.area_start + blank
            blank_cols = self.get_cols(blank_start)
            for name, row in self.rows.items():
                avg_blank = self.calculate_avg_blank(blank_cols, row)
                include_row = False
                for col in area_cols:
                    sub = float(row[col]) - (avg_blank * mult_factor)
                    if sub < 0: # no neg areas
                        sub = 0
                    row[col] = sub
                    if sub > 0:
                        include_row = True
                if include_row:
                    row['avg_blank'] = avg_blank
                    subtracted[name] = row
            self.rows = subtracted

    def calculate_avg_blank(self, blank_cols, row):
            avg_blank = 0
            for col in blank_cols:
                avg_blank += float(row[col])
            return avg_blank / len(blank_cols)

    def remove_columns(self, remove_cols):
        if self.rows:
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

    def normalize(self, data):
        if self.rows:
            normal = self.rows
            if data['normalize'] != 'none':
                area_cols = self.get_cols(self.area_start)
                if data['normalize'] == 'values':
                    for name, row in normal.items():
                        for col in area_cols:
                            group, num = self.get_group_from_area(col)
                            form_name = 'normal_' + group
                            if data[form_name]:
                                normal[name][col] = row[col] / float(data[form_name])
                elif data['normalize'] == 'blank' and data['blank']:
                    for name, row in normal.items():
                        for col in area_cols:
                            normal[name][col] = row[col]/row['avg_blank']
                    self.recalc_cols()
            self.rows = normal

    def get_groups(self):
        groups = {}
        area_cols = self.get_cols(self.area_start)
        for a_col in area_cols:
            group, num = self.get_group_from_area(a_col)
            if group not in groups:
                groups[group] = []
            groups[group].append(num)
        return groups

    def get_group_from_area(self, col):
        gr = col.split('[')[1]
        gr = gr.split('-')
        num = gr[1].split(']')[0]
        return gr[0], num

    def recalc_cols(self):
        self.groups = self.get_groups()
        stats = {}
        for name, row in self.rows.items():
            for group, nums in self.groups.items():
                if group not in stats:
                    stats[group] = []
                for num in nums:
                    num_col = self.area_start + group + '-' + num + ']'
                stats[group].append(row[num_col])
            for group, val_lst in stats.items():
                self.rows[name]['GroupArea[' + group + ']'] = numpy.mean(val_lst)
                self.rows[name]['GroupRSD[' + group + ']'] = numpy.std(val_lst)



