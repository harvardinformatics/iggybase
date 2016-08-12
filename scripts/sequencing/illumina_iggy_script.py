import sys
import os

# add iggybase root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import datetime
import json
from dateutil.relativedelta import relativedelta
import glob
from xml.etree import ElementTree
import csv
from scripts.iggy_script import IggyScript
import illumina_iggy_config as config

"""
script for inserting illumina_run data

CLI options include
    --insert_mode: will actually do the inserts
    --path: path to the file containing directories of illumina data
    --filename: what file to process, exp RunInfo.xml

exp use:
python process_illumina_data.py --insert_mode --path='/n/seq/sequencing/'
    --filename=RunInfo.xml
"""

class IlluminaIggyScript (IggyScript):
    def __init__(self):
        super(IlluminaIggyScript, self).__init__(config)

    def parse_illumina_run(self, data, pk):
        machine = self.pk_exists(data.findall('Instrument')[0].text, 'name', 'machine')
        row_dict = {
            'name': pk,
            'number': data.attrib.get('Number'),
            'machine_id': machine,
            'status': 'new'
        }
        for read in data.findall('Reads')[0].findall('Read'):
            num = read.attrib.get('Number')
            prefix = 'read_' + num
            row_dict[prefix + '_cycles'] = read.attrib.get('NumCycles')
            if read.attrib.get('IsIndexedRead') == 'Y':
                index = 1
            else:
                index = 0
            row_dict[prefix + '_index'] =  index
        return row_dict

    def parse_illumina_flowcell(self, data, pk):
        flowcell_layout = data.findall('FlowcellLayout')[0]
        row_dict = {
            'name': pk,
            'lane_count': flowcell_layout.get('LaneCount'),
            'surface_count': flowcell_layout.get('SurfaceCount'),
            'swath_count': flowcell_layout.get('SwathCount'),
            'tile_count': flowcell_layout.get('TileCount'),
            'status': 'new'
        }
        return row_dict

    def parse_sample_sheet(self, data, file):
        data_split = data.split('_')
        machine_id = self.pk_exists(data_split[1], 'name', 'machine')
        flowcell_id = self.pk_exists(data_split[3][1:], 'name', 'illumina_flowcell')
        run_id = self.pk_exists(flowcell_id, 'id', 'illumina_flowcell', 'illumina_run_id')
        row_dict = {
            'name': data,
            'run_date': (data_split[0][2:4] + '/' + data_split[0][4:6] + '/' + data_split[0][0:2]),
            'machine_id': machine_id,
            'slot': data_split[3][0:1],
            'illumina_flowcell_id': flowcell_id,
            'illumina_run_id': run_id,
            'file': file,
            'date_created': 'now'
        }
        return row_dict

    def parse_sample_sheet_item(self, data):
        row_dict = {
            'index': data['index'],
            'order_id': data['order_id'],
            'sample_sheet_id': data['sample_sheet_id'],
            'date_created': 'now'
        }
        if 'lane' in data:
            row_dict['lane'] = data['lane']
        return row_dict

    def get_sample_sheet_item_id(self, run_id, order_id, index, lane = None):
        sql = ('select i.id from sample_sheet_item i'
            ' inner join sample_sheet s on i.sample_sheet_id = s.id'
            ' where s.illumina_run_id = ' + str(run_id)
            + ' and i.order_id = ' + str(order_id)
            + ' and i.index = "' + index + '"')
        if lane:
            sql += ' and i.lane = ' + lane
        print("\t\t" + sql)
        exist = self.db.cursor()
        exist.execute(sql)
        row = exist.fetchone()
        row_id = None
        if row:
            row_id = row[0]
        return row_id

    def insert_sample_sheet_items(self, rows):
        inserted = 0
        skipped = 0
        failed = 0
        si_table = 'sample_sheet_item'
        print("\t\tfound " + str(len(rows)) + ' sample sheet items to enter')
        for row in rows:
            if row['illumina_run_id'] and row['order_id'] and row['index']:
                row_id = self.get_sample_sheet_item_id(
                        row['illumina_run_id'],
                        row['order_id'],
                        row['index'],
                        row.get('lane', None)
                )
                if not row_id:
                    row_dict = self.parse_sample_sheet_item(row)
                    name, next_num = self.get_next_name(si_table)
                    row_dict.update({'name': name})
                    si_id = self.do_insert(si_table, row_dict)
                    if si_id:
                        update_row(
                                'table_object',
                                {'name': si_table},
                                {'new_name_id': next_num}
                        )
                        inserted += 1
                else:
                    skipped += 1
            else:
                print("\t\tnot enough infomation provided")
                failed += 1
            print("\n\n")
        print("\t\tinserted " + str(inserted)
                + " skipped " + str(skipped)
                + " failed " + str(failed)
                + " total = " + str(inserted + skipped + failed)
                + " sample sheet items out of " + str(len(rows)))

    def parse_hiseq(self, lines, illumina_run_id, ss_id):
        item_cols = [i.lower() for i in lines[0]]
        rows = []
        order_ids = []
        for row in lines[1:]:
            row_dict = dict(zip(item_cols, row))
            if 'description' in row_dict:
                order_id = self.pk_exists(row_dict['description'], 'name', 'order')
                if order_id:
                    order_ids.append(order_id)
            row_dict.update({
                'order_id': order_id,
                'sample_sheet_id': ss_id,
                'illumina_run_id': illumina_run_id
            })
            rows.append(row_dict)
        return order_ids, rows

    def parse_miseq(self, file_dict, illumina_run_id, ss_id):
        order_ids = []
        if 'header' in file_dict and file_dict['header'][2][1]:
            order_id = self.pk_exists(file_dict['header'][2][1], 'name', 'order')
        rows = []
        if order_id:
            item_cols = [i.lower() for i in file_dict['data'][0]]
            for row in file_dict['data'][1:]:
                row_dict = dict(zip(item_cols, row))
                row_dict.update({
                    'order_id': order_id,
                    'illumina_run_id': illumina_run_id,
                    'sample_sheet_id': ss_id
                })
                rows.append(row_dict)
            order_ids.append(order_id)
        return order_ids, rows

    def process_file_runinfo(self, file):
        run_info = ElementTree.parse(file).getroot()
        print("\tprocessing " + str(len(run_info)) + ' runs')
        for run in run_info:
            run_table = 'illumina_run'
            run_name = run.attrib.get('Id')
            run_id = self.row_exists(run_table, run_name)
            if not run_id:
                row_dict = self.parse_illumina_run(run, run_name)
                if row_dict:
                    run_id = self.do_insert(run_table, row_dict)
            if run_id:
                flow_table = 'illumina_flowcell'
                flow_name = run.findall('Flowcell')[0].text
                flow_id = self.row_exists(flow_table, flow_name)
                if not flow_id:
                    row_dict = self.parse_illumina_flowcell(run, flow_name)
                    if row_dict:
                        row_dict.update({'illumina_run_id': run_id})
                        self.do_insert(flow_table, row_dict)

    def process_file_samplesheet(self, file):
        ss_name = (file.replace(self.cli['path'], '')
            .replace(self.cli['filename'], '')
            .replace('/', ''))

        ss_table = 'sample_sheet'
        ss_id = self.row_exists(ss_table, ss_name)
        ss_dict = self.parse_sample_sheet(ss_name, file)
        if ss_dict:
            contents = open(file, 'rt')
            illumina_run_id = ss_dict['illumina_run_id']
            try:
                lines = list(csv.reader(contents))
                if lines[0][0] == '[Header]':
                    file_dict = {}
                    for row in lines:
                        if row and '[' in row[0]:
                            header = row[0].replace('[', '').replace(']', '').lower()
                        elif header and row:
                            if header in file_dict:
                                file_dict[header].append(row)
                            else:
                                file_dict[header] = [row]
                    if ('settings' in file_dict):
                        count = len(file_dict['settings'])
                        if file_dict['settings'][0] and file_dict['settings'][0][0].lower() == 'adapter':
                            ss_dict['adapter_1'] = file_dict['settings'][0][1]
                        # TODO: consider max here or create new table
                        '''if count > 1:
                            adaptor_num = 2
                            for setting in file_dict['settings'][1:]:
                                if len(setting) > 1:
                                    ss_dict['adapter_' + adaptor_num] = setting[1]
                                adaptor_num += 1 '''
                    if ('reads' in file_dict
                            and file_dict['reads']
                            and file_dict['reads'][0]
                    ):
                        ss_dict['read_length_1'] = file_dict['reads'][0][0]
                    if not ss_id:
                        ss_id = self.do_insert(ss_table, ss_dict)
                    order_ids, rows = self.parse_miseq(file_dict, illumina_run_id, ss_id)
                else:
                    if not ss_id:
                        ss_id = self.do_insert(ss_table, ss_dict)
                    order_ids, rows = self.parse_hiseq(lines, illumina_run_id, ss_id)
                if ss_id:
                    self.insert_sample_sheet_items(rows)
                if order_ids:
                    if self.folder == 'primary_data':
                        self.update_table_status('order', list(set(order_ids)), 'running', ['new'])
                    else:
                        self.update_table_status('order', list(set(order_ids)), 'in analysis', ['new',
                        'running'])
            finally:
                contents.close()

    def parse_cli(self):
        cli = super(IlluminaIggyScript, self).parse_cli()
        if not 'path' in cli:
            # TODO: replace with real default after testing
            cli['path'] = '/Users/portermahoney/sites/primary_data'
        self.folder = cli['path'].split('/')[-1]

        if not 'filename' in cli:
            print('You must have the option filename, exp:'
                + ' python process_seq_file.py --path=~sites/analysis_finished'
                + ' --filename=RunInfo.xml')
            sys.exit(1)
        if not 'dir_match' in cli:
            cli['dir_match'] = ''
        return cli


    def run(self):
        # check path for filename
        print('Checking for filename: ' + self.cli['filename'] + ' in dir: ' + self.cli['path'])
        today = datetime.datetime.now()
        yesterday = today + relativedelta(days=-1)
        # within two days, TODO: days could be a cli
        days = [today.strftime("%y%m%d"), yesterday.strftime("%y%m%d")]
        days = ['160720', '160721'] # TODO: remove, this is for testing
        files = []
        for day in days:
            file_path = self.cli['path'] + '/' + day + '*' + self.cli['dir_match'] + '*/' + self.cli['filename']
            files.extend(glob.glob(file_path))
        print("\tfound " + str(len(files)) + " files to process")
        process_func = getattr(self, 'process_file_' + (self.cli['filename'].split('.')[0].lower()))

        for file in files:
            print("\tstarting to process: " + file)
            process_func(file)
            print("\n\n\n\n")
