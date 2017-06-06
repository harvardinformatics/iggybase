import sys
import os

# add iggybase root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import datetime
import re
import time
import json
from dateutil.relativedelta import relativedelta
import glob
from xml.etree import ElementTree
import csv
from scripts.iggy_script import IggyScript
import murray_config as config

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

class MigrateGenotype (IggyScript):
    def __init__(self):
        super(MigrateGenotype, self).__init__(config)
        self.to_db = self.db

    def parse_cli(self):
        cli = super(MigrateGenotype, self).parse_cli()
        if not 'filename' in cli:
            print('You must have the option filename, exp:'
                + ' python migrate_genotype.py --filename=MurrayStrainsOldPeeps')
            sys.exit(1)
        return cli

    def run(self):
        print('test')
        self.parse_xml(self.cli['filename'])

    def parse_xml(self, file):
        xml = ElementTree.parse(file).getroot()
        res = xml.find('RESULTSET')
        for row in res.findall('ROW'):
            row_id = row.attrib.get('RECORDID')
            cols = row.findall('COL')
            genotype = []
            name = cols[1].findall('DATA')[0].text
            geno = cols[9]
            datas = geno.findall('DATA')
            for data in datas:
                if data.text:
                    genotype.append(data.text)
            geno_str = '  '.join(genotype)
            geno_str = geno_str.replace('"', '')
            if geno_str and name:
                self.update_genotype(geno_str, name)

    def update_genotype(self, geno, name):
        strain_id = self.pk_exists(name, 'name', 'strain')
        if strain_id:
            self.update_row(
                    'strain',
                    {'id': strain_id},
                    {'genotype': geno}
            )

# execute run on this class
script = MigrateGenotype()
script.run()
