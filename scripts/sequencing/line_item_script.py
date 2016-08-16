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

class LineItemScript (IggyScript):
    def __init__(self):
        super(LineItemScript, self).__init__()

    def parse_cli(self):
        cli = super(LineItemScript, self).parse_cli()
        '''if not 'path' in cli:
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
        return cli'''

    def get_billable_lanes(self):
        sql = ('select l.id from lane l'
            + ' inner join sample_sheet_item i on i.lane_id = l.id'
            + ' inner join sample_sheet s on i.sample_sheet_id = s.id'
            + ' inner join illumina_run r on s.illumina_run_id = r.id'
            + ' inner join `order` o on i.order_id = o.id'
            + ' left join line_item t on t.row_id = l.id'
            + ' left join table_object b on t.table_object_id = b.id'
            + ' and b.name = "lane"'
            + ' where t.id is null'
            + ' and l.passed = 1'
            + ' and r.passed = 1'
            + ' and o.billable = 1')
        print("\t\t" + sql)
        exist = self.db.cursor()
        exist.execute(sql)
        rows = exist.fetchall()
        return rows

    def parse_line_item(self, lane):
        tbl = 'line_item'
        table_object_id = self.pk_exists('lane', 'name', 'table_object')
        name, next_num = self.get_next_name('line_item')
        row_dict = {
            'name': name,
            'table_object_id': table_object_id,
            'row_id': lane[0]
        }
        return row_dict


    def run(self):
        # check path for filename
        print('Checking for billable lanes')
        lanes = self.get_billable_lanes()
        for lane in lanes:
            print("\tstarting to process lane: " + lane[0])
            row_dict = self.parse_line_item(lane)
            print("\n\n\n\n")

# call run on this class
script = LineItemScript()
script.run()
