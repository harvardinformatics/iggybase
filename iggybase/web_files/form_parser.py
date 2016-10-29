import re
import os
from werkzeug.utils import secure_filename
from iggybase.core.data_instance import DataInstance
from iggybase import utilities as util
from flask import request, g, current_app
import logging


class FormParser():
    def __init__(self, table_name):
        self.table_name = table_name
        self.table_names = []
        self.instance = None

    def parse(self, form_data = None):
        # fields contain the data that was displayed on the form and possibly edited
        fields = {}

        web_request = False
        if not form_data:
            web_request = True
            form_data = request.form

        # used to identify fields that contain data that needs to be saved
        field_pattern = \
            re.compile('^(files_data_entry|id_data_entry|long_text|data_entry|record_data|form_data)_(\S+)_(\d+)')
        for key in form_data:
            if web_request:
                data = request.form.get(key)
            else:
                data = form_data[key]

            if key.startswith('bool_'):
                key = key[key.index('_') + 1:]

            field_id = field_pattern.match(key)
            if field_id is not None:
                if field_id.group(3) not in fields.keys():
                    fields[field_id.group(3)] = {'long_text': {}, 'form_data': {}, 'data_entry': {}, 'record_data': {},
                                                 'id_data_entry': {}, 'files_data_entry': {}}

                fields[field_id.group(3)][field_id.group(1)][field_id.group(2)] = data

        if request.files:
            files = request.files

            # http://werkzeug.pocoo.org/docs/0.11/datastructures/#werkzeug.datastructures.FileStorage
            for key in files:
                if files[key] and util.allowed_file(files[key].filename):
                    field_id = field_pattern.match(files[key].name)

                    filename = secure_filename(files[key].filename)

                    if field_id.group(2) not in fields[field_id.group(3)][field_id.group(1)]:
                        fields[field_id.group(3)][field_id.group(1)][field_id.group(2)] = {}

                    fields[field_id.group(3)][field_id.group(1)][field_id.group(2)][filename] = files[key]

        # for key1, value1 in fields.items():
        #     for key2, value2 in value1.items():
        #         for key3, value3 in value2.items():
        #            logging.info(str(key1) + ' ' + str(key2) + ' ' + str(key3) + ': ' + str(value3))

        self.instance = DataInstance(self.table_name, None, int(fields['0']['form_data']['max_level']))
        self.instance.get_data(fields['0']['form_data']['row_name'])

        for row_id in sorted(fields.keys()):
            row_data = fields[row_id]

            table_name_field = row_data['record_data']['table']
            if table_name_field not in self.table_names:
                self.table_names.append(table_name_field)

            if row_data['record_data']['new'] == '1':
                instance_name = self.instance.add_new_instance(table_name_field, 'new')
                if row_data['data_entry']['name'] != '' and row_data['data_entry']['name'] != 'new':
                    instance_name = row_data['data_entry']['name']
                else:
                    fields[row_id]['data_entry']['name'] = instance_name
            else:
                # on a multiform all instances are not fetched with get_data
                if row_data['record_data']['row_name'] not in self.instance.instances[table_name_field]:
                    instance_name = self.instance.add_new_instance(table_name_field,
                                                                   row_data['record_data']['row_name'])
                else:
                    instance_name = row_data['record_data']['row_name']

            if ('organization_id' in row_data['data_entry'].keys() and
                    row_data['data_entry']['organization_id']):
                row_org_id = row_data['data_entry']['organization_id']

                if not isinstance(row_org_id, int):
                    row_org_id = self.instance.set_foreign_key_field_id(table_name_field, 'organization_id', row_org_id)

            if row_org_id is None:
                if self.instance.get_value('organization_id', table_name_field, instance_name) is not None:
                    row_org_id = self.instance.get_value('organization_id')
                elif self.instance.organization_access_control.current_org_id is not None:
                    row_org_id = g.current_org_id
                else:
                    row_org_id = 1

            row_data['data_entry']['organization_id'] = row_org_id

            exclude_list = ['id', 'last_modified', 'date_created', 'organization_id']

            for table_field, meta_data in self.instance.fields[table_name_field].fields.items():
                # only update fields that were on the form
                if meta_data.Field.display_name not in row_data['data_entry'].keys():
                    continue

                field_data = meta_data.Field
                field = field_data.display_name

                if 'text' == meta_data.DataType.name.lower and row_data['data_entry'][field] != '':
                    if row_data['long_text'][field] == '':
                        lt = DataInstance('long_text', 'new')
                    else:
                        lt = DataInstance('long_text')
                        lt.get_data(None, int(row_data['long_text'][field]))

                    lt.set_value('organization_id', row_org_id)
                    lt.set_value('long_text', row_data['data_entry'][field])
                    msg = lt.save()

                    row_data['data_entry'][field] = next(iter(msg))
                elif field_data.foreign_key_table_object_id is not None:
                    try:
                        if row_data['data_entry'][field] is None or row_data['data_entry'][field] == '' \
                                or int(row_data['data_entry'][field]) == -99:
                            row_data['data_entry'][field] = None
                        else:
                            row_data['data_entry'][field] = int(row_data['data_entry'][field])
                    except (ValueError, KeyError) as e:
                        try:
                            row_data['data_entry'][field] = int(row_data['id_data_entry'][field])
                        except  (ValueError, KeyError) as e:
                            row_data['data_entry'][field] = None
                elif meta_data.DataType.name.lower() == 'file':
                    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], table_name_field,
                                             self.instance.instance_name)
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    old_files = []
                    if row_data['files_data_entry'][field] != "":
                        old_files = row_data['files_data_entry'][field].split("|")

                    if request.files:
                        for filename, file in row_data['data_entry'][field].items():
                            if os.path.exists(os.path.join(directory, filename)):
                                os.remove(os.path.join(directory, filename))
                                file.save(os.path.join(directory, filename))
                            else:
                                file.save(os.path.join(directory, filename))
                                old_files.append(filename)

                    if len(old_files) > 0:
                        filenames = "|".join(old_files)
                        row_data['data_entry'][field] = filenames
                elif field not in exclude_list:
                    if row_data['data_entry'][field] == '':
                        row_data['data_entry'][field] = None
                    elif field_data.data_type_id == 1:
                        row_data['data_entry'][field] = int(row_data['data_entry'][field])
                    elif field_data.data_type_id == 8:
                        row_data['data_entry'][field] = float(row_data['data_entry'][field])
                    elif field_data.data_type_id == 3:
                        if row_data['data_entry'][field] == 'y' or row_data['data_entry'][field] == 'True':
                            row_data['data_entry'][field] = True
                        else:
                            row_data['data_entry'][field] = False

            self.instance.set_values(row_data['data_entry'], table_name_field, instance_name)

    def save(self):
        commit_status, commit_msg = self.instance.commit()

        if commit_status is True:
            current_app.cache.increment_version(list(self.table_names))

        return commit_status, commit_msg

    def undo(self):
        self.instance.rollback()