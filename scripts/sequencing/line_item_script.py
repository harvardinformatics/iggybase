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
        return cli

    def get_billable_run_orders(self):
        sql = ('select r.id, o.id, i.id, s.id, m.machine_type_id, g.organization_type_id, o.organization_id from sample_sheet_item i'
            + ' inner join sample_sheet s on i.sample_sheet_id = s.id'
            + ' inner join illumina_run r on s.illumina_run_id = r.id'
            + ' inner join machine m on r.machine_id = m.id'
            + ' inner join `order` o on i.order_id = o.id'
            + ' inner join organization g on g.id = o.organization_id '
            + ' left join ('
            + ' select t.order_id as t, a.row_id as a from line_item t'
            + ' left join line_item_assoc a on t.id = a.line_item_id'
            + ' left join table_object b on a.table_object_id = b.id'
            + ' and b.name = "illumina_run"'
            + ') as line on r.id = line.a and o.id = line.t'
            + ' where r.passed = 1'
            + ' and o.billable = 1'
            + " and o.date_created > '2016-08-01 01:00:01'"
            + ' and line.t is null')
        print("\t\t" + sql)
        exist = self.db.cursor()
        exist.execute(sql)
        rows = exist.fetchall()
        return rows

    def parse_line_item(self, price_item_id, price, order_id, organization_id):
        row_dict = {
                'price_item_id': price_item_id,
                'price_per_unit': float(price),
                'quantity': 1,
                'order_id': order_id,
                'date_created': 'now',
                'organization_id': organization_id
        }
        return row_dict

    def parse_line_item_assoc(self, line_item_id, run_id):
        table_object_id = self.pk_exists('illumina_run', 'name', 'table_object')
        row_dict = {
                'line_item_id': line_item_id,
                'row_id': run_id,
                'table_object_id': table_object_id
        }
        return row_dict

    def parse_ro(self, row):
        row_dict = {
                'run_id': row[0],
                'order_id': row[1],
                'ss_item_id': row[2],
                'ss_id': row[3],
                'machine_type_id': row[4],
                'organization_type_id': row[5],
                'organization_id': row[6]
        }

        depth = self.get_sample_data(row_dict['order_id'])
        row_dict['depth'] = depth
        lane_id = self.get_lane_id(row_dict['ss_item_id'])
        row_dict['lane_id'] = lane_id
        read_num, length = self.get_read_info(row_dict['ss_id'])
        row_dict['read_num'] = read_num
        row_dict['length'] = length
        return row_dict

    def get_read_info(self, ss_id):
        sql = ('select count(re.id) as read_num, max(re.cycles) as length from `read` re'
                + ' inner join sample_sheet s'
                + ' on s.illumina_run_id = re.illumina_run_id'
                + ' where s.id = ' + str(ss_id) + ' and re.indexed = 0')
        print("\t\t" + sql)
        exist = self.db.cursor()
        exist.execute(sql)
        rows = exist.fetchone()
        read_num = rows[0]
        length = rows[1]
        return read_num, length

    def get_lane_id(self, ss_item_id):
        sql = ('select l.id from lane l'
                + ' inner join sample_sheet_item i on i.lane_id = l.id'
                + ' where i.id = ' + str(ss_item_id))
        print("\t\t" + sql)
        exist = self.db.cursor()
        exist.execute(sql)
        row = exist.fetchone()
        return row[0]

    def get_sample_data(self, order_id):
        sql = ('select r.depth from sample s'
                + ' inner join line_item l on s.line_item_id = l.id'
                + ' inner join run_type r on s.run_type_id = r.id'
                + ' where l.order_id = ' + str(order_id)
                + ' and s.read_length is not null')
        print("\t\t" + sql)
        exist = self.db.cursor()
        exist.execute(sql)
        row = exist.fetchone()
        depth = None
        if row:
            depth = row[0]
        return depth

    def get_service(self, organization_type_id, length, lane_number, machine_type_id, read_number, depth):
        sql = ('select p.id, l.price_per_unit, s.max_length from sequencing_service s'
                + ' inner join price_item_assoc a on a.row_id = s.id'
                + ' inner join price_item p on p.id = a.price_item_id'
                + ' inner join table_object t on t.id = a.table_object_id'
                + ' inner join price_list l on p.id = l.price_item_id '
                + ' where s.lane_number = ' + str(lane_number)
                + ' and s.machine_type_id = ' + str(machine_type_id)
                + ' and s.read_number = ' + str(read_number)
                + ' and l.organization_type_id = ' + str(organization_type_id)
                + ' and t.name = "sequencing_service"')
        if depth:
            sql += ' and s.depth = "' + depth + '"'
        sql += ' order by max_length desc'

        print("\t\t" + sql)
        exist = self.db.cursor()
        exist.execute(sql)
        rows = exist.fetchall()
        max_length = None
        service_id = None
        for row in rows:
            if not max_length:
                max_length = row[2]
                service_id = row[0]
                price = row[1]
            else:
                if row[2] >= length and row[2] < max_length:
                    max_length = row[2]
                    service_id = row[0]
                    price = row[1]
        return service_id, price

    def run(self):
        # check path for filename
        print('Checking for billable lanes')
        res = self.get_billable_run_orders()
        print("\tFound billable lanes: " + str(len(res)))
        ros = {}
        for row in res:
            run_order = str(row[0]) +  '_' + str(row[1])
            row_dict = self.parse_ro(row)
            if run_order in ros:
                ros[run_order].append(row_dict)
            else:
                ros[run_order] = [row_dict]
        for ro, rows in ros.items():
            print("\t\tstarting to process run_order: " + ro)
            run_id = ro[0]
            order_id = ro[1]
            service_params = {}
            lanes = set([])
            for i, row in enumerate(rows):
                if i == 0:
                    service_params = row
                lanes.add(row['lane_id'])
            service_params['lane_num'] = len(list(lanes))
            if service_params['lane_num'] > 2:
                service_params['lane_num'] = 8
            price_item_id, price = self.get_service(
                    service_params['organization_type_id'],
                    service_params['length'],
                    service_params['lane_num'],
                    service_params['machine_type_id'],
                    service_params['read_num'],
                    service_params['depth']
            )
            line_item_table = 'line_item'
            row_dict = self.parse_line_item(price_item_id, price, order_id, rows[0]['organization_id'])
            name, next_num = self.get_next_name(line_item_table)
            row_dict.update({'name': name})
            line_item_id = self.do_insert(line_item_table, row_dict)
            if line_item_id:
                self.update_row(
                        'table_object',
                        {'name': line_item_table},
                        {'new_name_id': next_num}
                )
                assoc_table = 'line_item_assoc'
                assoc_dict = self.parse_line_item_assoc(line_item_id, run_id)
                name, next_num = self.get_next_name(assoc_table)
                assoc_dict.update({'name': name})
                assoc_id = self.do_insert(assoc_table, assoc_dict)
                if assoc_id:
                    self.update_row(
                            'table_object',
                            {'name': assoc_table},
                            {'new_name_id': next_num}
                    )
            print("\n\n\n\n")

# call run on this class
script = LineItemScript()
script.run()
