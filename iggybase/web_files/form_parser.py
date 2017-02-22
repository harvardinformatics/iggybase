import re
import os
import datetime
from werkzeug.utils import secure_filename
from iggybase.core.instance_collection import InstanceCollection
from iggybase import utilities as util
from flask import request, current_app, session
import logging


class FormParser():
    def __init__(self, table_name):
        self.table_name = table_name
        self.table_names = []
        self.instance = None
        self.files = {}

    def parse(self, form_data = None):
        logging.info('parser called')
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
                # TODO: The different types of information being stored in this
                # multilevel array could be made parts of an object
                if field_id.group(3) not in fields.keys():
                    fields[field_id.group(3)] = {'long_text': {}, 'form_data': {}, 'data_entry': {}, 'record_data': {},
                                                 'id_data_entry': {}, 'files_data_entry': {}}

                fields[field_id.group(3)][field_id.group(1)][field_id.group(2)] = data

        if request.files:
            # http://werkzeug.pocoo.org/docs/0.11/datastructures/#werkzeug.datastructures.FileStorage
            files = request.files

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

        self.instance = InstanceCollection(int(fields['0']['form_data']['max_level']), {self.table_name: []} )

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
                if row_data['record_data']['row_name'] not in self.instance.instances:
                    instance_name = self.instance.add_new_instance(table_name_field,
                                                                   row_data['record_data']['row_name'])
                else:
                    instance_name = row_data['record_data']['row_name']

            # logging.info("row_data['record_data']['new']: " + str(row_data['record_data']['new']) +
            #              "   instance_name: " + instance_name +
            #              "   row_data['record_data']['row_name']: " + str(row_data['record_data']['row_name']))

            if ('organization_id' in row_data['data_entry'].keys() and
                    row_data['data_entry']['organization_id']):
                row_org_id = row_data['data_entry']['organization_id']

                if not isinstance(row_org_id, int):
                    row_org_id = self.instance.set_foreign_key_field_id(table_name_field, 'organization_id', row_org_id)

            if row_org_id is None:
                if self.instance[instance_name] and self.instance[instance_name].organization_id:
                    row_org_id = self.instance[instance_name].organization_id
                elif self.instance.organization_access_control.current_org_id is not None:
                    row_org_id = session['org_id']['current_org_id']
                else:
                    row_org_id = 1

            row_data['data_entry']['organization_id'] = row_org_id

            for table_field, meta_data in self.instance.tables[table_name_field].fields.items():
                # only update fields that were on the form
                if meta_data.Field.display_name not in row_data['data_entry'].keys():
                    continue

                field_data = meta_data.Field
                field = field_data.display_name

                # handle empty and FK
                if row_data['data_entry'][field] == '':
                    row_data['data_entry'][field] = None
                elif meta_data.type == 'text' and row_data['data_entry'][field] is not None:
                    logging.info('long text: ' + str(row_data['data_entry'][field]))

                    if row_data['long_text'][field] == '':
                        lt_name = 'new'
                    else:
                        lt_name = row_data['long_text'][field]

                    lt = InstanceCollection(0, {'long_text': lt_name})
                    lt_name = list(lt.keys())[0]

                    lt.set_value(lt_name, 'organization_id', row_org_id)
                    lt.set_value(lt_name, 'long_text', row_data['data_entry'][field])
                    commit_status, msg = lt.commit()
                    logging.info(msg)
                    row_data['data_entry'][field] = list(msg.keys())[0]
                elif field_data.foreign_key_table_object_id is not None:
                    try:
                        row_data['data_entry'][field] = int(row_data['id_data_entry'][field])
                    except (ValueError, KeyError) as e:
                        try:
                            if row_data['data_entry'][field] is None or row_data['data_entry'][field] == '' \
                                    or int(row_data['data_entry'][field]) == -99:
                                row_data['data_entry'][field] = None
                            else:
                                row_data['data_entry'][field] = int(row_data['data_entry'][field])
                        except (ValueError, KeyError) as e:
                            row_data['data_entry'][field] = None
                # handle datatypes
                elif meta_data.type == 'integer':
                    row_data['data_entry'][field] = int(row_data['data_entry'][field])
                elif meta_data.type == 'boolean':
                    if row_data['data_entry'][field] == 'y' or row_data['data_entry'][field] == 'True' or \
                                    row_data['data_entry'][field] == '1':
                        row_data['data_entry'][field] = True
                    else:
                        row_data['data_entry'][field] = False
                elif meta_data.type == 'datetime':
                    date = None
                    try:
                        date = datetime.strptime(row_data['data_entry'][field],'%Y-%d-%m %T')
                    except:
                        try:
                            date = datetime.strptime(row_data['data_entry'][field],'%Y-%d-%m')
                        except:
                            pass
                            # logging.info('Failed to parse date:' + row_data['data_entry'][field])
                    row_data['data_entry'][field] = date
                elif meta_data.type == 'float':
                    row_data['data_entry'][field] = float(row_data['data_entry'][field])
                elif meta_data.type == 'file':
                    old_files = []
                    self.files[(instance_name, table_name_field)] = []

                    if row_data['files_data_entry'][field] != "":
                        old_files = row_data['files_data_entry'][field].split("|")

                    if request.files:
                        for filename, file in row_data['data_entry'][field].items():
                            self.files[(instance_name, table_name_field)].append({'filename': filename, 'file': file})

                            if filename not in old_files:
                                old_files.append(filename)

                    if len(old_files) > 0:
                        filenames = "|".join(old_files)
                        row_data['data_entry'][field] = filenames

            self.instance.set_values(instance_name, row_data['data_entry'])

    def save(self):
        commit_status, commit_msg = self.instance.commit()

        if commit_status is True:
            for key in set(self.files) & set(self.instance.instance_names):
                for file_data in self.files[key]:
                    directory = (os.path.join(current_app.config['UPLOAD_FOLDER'], key[1],
                                              self.instance.instance_names[key])).strip()

                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    if os.path.exists(os.path.join(directory, file_data['filename'])):
                        os.remove(os.path.join(directory, file_data['filename']))

                    file_data['file'].save(os.path.join(directory, file_data['filename']))

            current_app.cache.increment_version(list(self.table_names))

        return commit_status, commit_msg

    def undo(self):
        self.instance.rollback()
