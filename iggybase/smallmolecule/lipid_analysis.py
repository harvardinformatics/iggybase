import csv
import os
import numpy
import zipfile
from flask import request
from flask.ext import excel
from config import Config
from collections import OrderedDict

class LipidAnalysis:
    def __init__ (self, paths):
        self.paths = paths
        self.area_start = 'Area['
        self.groups = {}
        self.rows = self.get_rows_from_files(self.paths)
        self.debug = ('debug' in request.args)

        # file paths, eventualy these may not be hardcoded
        self.root_path = Config.UPLOAD_FOLDER + '/lipid_analysis/'
        lipid_class_file = 'lipidKey.csv'
        self.lipid_class_path = self.root_path + lipid_class_file
        self.lipid_results_file = 'lipid_analysis.csv'
        self.lipid_results_path = self.root_path + self.lipid_results_file
        self.subclass_file = 'subclass_stats.csv'
        self.subclass_path = self.root_path + self.subclass_file
        self.class_file = 'class_stats.csv'
        self.class_path = self.root_path + self.class_file
        zip_file = 'lipid_results.zip'
        self.zip_path = self.root_path + zip_file

    def get_rows_from_files(self, paths):
        rows = OrderedDict()
        cols = []
        for path in paths:
            if path:
                with open(path,'r') as f:
                    for i,ln in enumerate(f):
                        if i == 0:
                            row_cols = []
                        if (ln.startswith('#') or ln.startswith('\t') or
                                ln.startswith('\n')):
                            continue
                        if not row_cols:
                            ln = ln.replace('\n', '')
                            row_cols = ln.split('\t')
                        else: # data lines
                            ln = ln.replace('\n', '')
                            row = ln.split('\t')
                            # remove trailing newline
                            row[(len(row) - 1)] = row[(len(row) - 1)].strip('\n')
                            row_d = OrderedDict(zip(row_cols, row))
                            ret_time = self.avg_col_type(row_d, 'GroupTopPos')
                            row_d['ret_time'] = ret_time
                            row_d.move_to_end('ret_time', last=False)
                            name = row_d['LipidIon'] + '_' + str(ret_time)
                            row_d['name'] = name
                            row_d.move_to_end('name', last=False)
                            row_d = self.clean_cols(cols, row_cols, row_d)
                            rows[name] = row_d
                    cols = row_cols
        return rows

    def clean_cols(self, cols, row_cols, row_d):
        if cols:
            # exclude any cols not in first file
            diff = [x for x in row_cols if x not in cols]
            for k in diff:
                del row_d[k]
        return row_d

    def get_cols(self, start = None):
        first = list(self.rows.keys())[0]
        keys = list(self.rows[first].keys())
        if start:
            keys = [i for i in keys if i.startswith(start)]
        return keys

    def write_results(self):
        self.write_csv(self.lipid_results_path, self.get_cols(),
                self.rows.values())
        # create a zip file for lipids and stats
        z = zipfile.ZipFile(self.zip_path, "w")
        z.write(self.lipid_results_path, self.lipid_results_file)
        z.write(self.subclass_path, self.subclass_file)
        z.write(self.class_path, self.class_file)
        z.close
        return self.zip_path

    def write_csv(self, path, cols, rows):
        success = False
        if self.rows:
            if not os.path.exists(self.root_path):
                os.makedirs(self.root_path)
            with open(path,'w') as c:
                w = csv.DictWriter(c, cols)
                w.writeheader()
                w.writerows(rows)
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
                            group, num = self.get_group_from_col(col)
                            form_name = 'normal_' + group
                            if data[form_name]:
                                if self.debug:
                                    normal[name][col + 'old'] = row[col]
                                    normal[name][col + 'div'] = float(data[form_name])
                                normal[name][col] = row[col] / float(data[form_name])
                elif data['normalize'] == 'intensity':
                    intensities = self.calc_intensities(area_cols)
                    for name, row in normal.items():
                        for col in area_cols:
                            sam = self.get_sample_from_col(col)
                            if intensities[sam] > 0:
                                if self.debug:
                                    normal[name][col + 'old'] = row[col]
                                    normal[name][col + 'div'] = intensities[sam]
                                normal[name][col] = row[col]/intensities[sam]
                self.recalc_cols()
            self.rows = normal

    def calc_intensities(self, area_cols):
        intensities = {}
        cnt = len(self.rows)
        for name, row in self.rows.items():
            for col in area_cols:
                sam = self.get_sample_from_col(col)
                if sam not in intensities:
                    intensities[sam] = 0
                intensities[sam] += row[col]
        for sam, i_sum in intensities.items():
            intensities[sam] = i_sum / cnt
        return intensities


    def get_groups(self):
        groups = OrderedDict()
        area_cols = self.get_cols(self.area_start)
        for a_col in area_cols:
            group, num = self.get_group_from_col(a_col)
            if group not in groups:
                groups[group] = []
            groups[group].append(num)
        return groups

    def get_group_from_col(self, col):
        gr = col.split('[')[1]
        gr = gr.split('-')
        num = gr[1].split(']')[0]
        return gr[0], num

    def get_sample_from_col(self, col):
        sam = col.split('[')[1]
        sam = sam.split(']')
        return sam[0]

    def recalc_cols(self):
        self.groups = self.get_groups()
        for name, row in self.rows.items():
            stats = OrderedDict()
            for group, nums in self.groups.items():
                if group not in stats:
                    stats[group] = []
                for num in nums:
                    num_col = self.area_start + group + '-' + num + ']'
                    stats[group].append(row[num_col])
            for group, val_lst in stats.items():
                self.rows[name]['GroupAVG[' + group + ']'] = numpy.mean(val_lst)
                self.rows[name]['GroupRSD[' + group + ']'] = numpy.std(val_lst)

    def calc_class_stats(self, class_stats):
        if class_stats:
            self.class_key = self.load_lipid_classes()
            class_stats = {}
            subclass_stats = {}
            for name, row in self.rows.items():
                sc = row['Class']
                if sc in self.class_key:
                    cl = self.class_key[sc]['class']
                    if sc not in subclass_stats:
                        subclass_stats[sc] = {}
                        if cl not in class_stats:
                            class_stats[cl] = {}
                    subclass_stats[sc] = self.group_stats(row,
                            subclass_stats[sc])
                    class_stats[cl] = self.group_stats(row,
                            class_stats[cl])
        subclass_cols, subclass_rows = self.format_stats('subclass', subclass_stats)
        sub_success = self.write_csv(self.subclass_path, subclass_cols, subclass_rows)
        class_cols, class_rows = self.format_stats('class', class_stats)
        class_success = self.write_csv(self.class_path, class_cols, class_rows)
        return sub_success, class_success

    def format_stats(self, cat, stats):
        rows = []
        cols = [cat]
        grps = self.get_groups()
        for g in grps:
            cols.append(g + ' cnt')
            cols.append(g + ' avg')
            cols.append(g + ' std')
        for cl, groups in stats.items():
            row = {}
            row[cat] = cl
            for name, info in groups.items():
                row[name + ' cnt'] = info['cnt']
                row[name + ' avg'] = numpy.mean(info['grp_areas'])
                row[name + ' std'] = numpy.std(info['grp_areas'])
            rows.append(row)
        return cols, rows

    def group_stats(self, row, grp_info):
        prefix = 'GroupArea'
        if not self.groups:
            self.groups = self.get_groups()
        for key in self.groups.keys():
            if key not in grp_info:
                grp_info[key] = {'cnt': 0, 'grp_areas': []}

            area_cols = self.get_cols(self.area_start + key)
            present = 0
            areas = []
            for col in area_cols:
                if float(row[col]) > 0.0:
                    present = 1
                areas.append(float(row[col]))
            grp_info[key]['cnt'] += present
            grp_info[key]['grp_areas'].append(numpy.mean(areas))
        return grp_info

    def load_lipid_classes(self):
        classes = {}
        with open(self.lipid_class_path,'r') as f:
            for i,ln in enumerate(f):
                ln = ln.replace('\n', '')
                ln = ln.rstrip(',')
                row = ln.split(',')
                if i == 0:
                    cols = [x.lower() for x in row]
                else:
                    row_dict = dict(zip(cols, row))
                    classes[row_dict['key']] = row_dict
        return classes
