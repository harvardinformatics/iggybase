import re
import os
from datetime import datetime
from decimal import Decimal
from werkzeug.utils import secure_filename
from iggybase.core.instance_collection import InstanceCollection
from iggybase import utilities as util
from flask import request, current_app, session
import logging


class FormParser():
    def __init__(self, table_name):
        self.table_name = table_name
        self.table_names = []
        self.instances = None
        self.files = {}
        self.fields = {}

    def parse(self, form_data = None):
        if form_data:
            web_request = False
            self.instances = InstanceCollection(int(form_data['max_depth']),
                                                {form_data['main_table']:[form_data['base_instance']]})
        else:
            web_request = True
            form_data = request.form
            self.instances = InstanceCollection(int(request.form.get('max_depth')),
                                                {request.form.get('main_table'):[request.form.get('base_instance')]})

        errors = {}
        instances = {}

        try:
            self.instances.instance_counter = int(request.form.get('row_counter'))
        except:
            self.instances.instance_counter = 1

        if self.instances.oac.current_org_id is not None:
            default_org_id = session['org_id']['current_org_id']
        else:
            default_org_id = 1

        # used to identify fields that contain data that needs to be saved
        field_pattern = re.compile('^(files_data_entry|data_entry)-(\S+)-(\S+)-(\S+)-(\d+)')

        for key in form_data:
            if web_request:
                data = request.form.get(key)
            else:
                data = form_data[key]

            if key.startswith('bool_'):
                key = key[key.index('_') + 1:]

            field_id = field_pattern.match(key)

            if field_id is not None:
                if (field_id.group(2), field_id.group(4)) not in instances.keys():
                    try:
                        instance_name = self.instances.add_instance(field_id.group(2), {'id': [int(field_id.group(4))]})
                    except (ValueError, KeyError) as e:
                        instance_name = self.instances.add_instance(field_id.group(2), {'name': [field_id.group(4)]})

                    self.instances[instance_name].form_index = field_id.group(5)
                    instances[(field_id.group(2), field_id.group(4))] = instance_name
                else:
                    instance_name = instances[(field_id.group(2), field_id.group(4))]

                new_key = (field_id.group(1) + "-" + field_id.group(2) + "-" + field_id.group(3) + "-" + instance_name +
                           "-" + field_id.group(5))

                field_name = field_id.group(3)
                table_name = field_id.group(2)

                if table_name not in self.table_names:
                    self.table_names.append(table_name)

                meta_data = self.instances.tables[table_name].fields[table_name + "|" + field_name]
                field_data = meta_data.Field

                # handle empty and FK
                if data == '':
                    if meta_data.FieldRole.required == 1:
                        errors[new_key] = "Field is required"
                        logging.info('required field not entered: ' + field_name)
                    self.instances.set_value(instance_name, field_name, None)
                elif field_data.foreign_key_table_object_id is not None:
                    try:
                        lookup_value = int(data)
                        if lookup_value == -99:
                            lookup_value = None
                    except (ValueError, KeyError):
                        try:
                            if data is None or data == '':
                                lookup_value = None
                            else:
                                if web_request:
                                    data = request.form.get('id_' + key)
                                else:
                                    data = form_data['id_' + key]

                                if data is None:
                                    lookup_value = data
                                else:
                                    lookup_value = int(data)
                        except (ValueError, KeyError):
                            lookup_value = None

                    if field_name == 'organization_id' and lookup_value is None:
                        lookup_value = default_org_id

                    self.instances.set_value(instance_name, field_name, lookup_value)
                # handle datatypes
                elif meta_data.type == 'integer':
                    try:
                        self.instances.set_value(instance_name, field_name, int(data))
                    except ValueError as e:
                        self.instances.set_value(instance_name, field_name, data)
                        errors[new_key] = e.args[0]
                        logging.info('Failed to parse int ' + field_name + ':' + str(data))
                        logging.info(format(e))
                elif meta_data.type == 'boolean':
                    if data in ['yes', 'y', 'True', True, 1, '1', 'on']:
                        self.instances.set_value(instance_name, field_name, True)
                    else:
                        self.instances.set_value(instance_name, field_name, False)
                elif meta_data.type == 'datetime':
                    try:
                        datetime_val = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                        self.instances.set_value(instance_name, field_name, datetime_val)
                    except ValueError as e:
                        self.instances.set_value(instance_name, field_name, data)
                        errors[new_key] = e.args[0]
                        logging.info('Failed to parse datetime ' + field_name + ':' + str(data))
                        logging.info(format(e))
                elif meta_data.type == 'date':
                    try:
                        date_val = datetime.strptime(data, '%Y-%m-%d')
                        self.instances.set_value(instance_name, field_name, date_val.date())
                    except ValueError as e:
                        self.instances.set_value(instance_name, field_name, data)
                        errors[new_key] = e.args[0]
                        logging.info('Failed to parse date ' + field_name + ':' + str(data))
                        logging.info(format(e))
                elif meta_data.type == 'float':
                    try:
                        self.instances.set_value(instance_name, field_name, float(data))
                    except ValueError as e:
                        self.instances.set_value(instance_name, field_name, data)
                        errors[new_key] = e.args[0]
                        logging.info('Failed to parse date ' + field_name + ':' + str(data))
                        logging.info(format(e))
                elif meta_data.type == 'decimal':
                    try:
                        self.instances.set_value(instance_name, field_name, Decimal(data))
                    except ValueError as e:
                        self.instances.set_value(instance_name, field_name, data)
                        errors[new_key] = e.args[0]
                        logging.info('Failed to parse date ' + field_name + ':' + str(data))
                        logging.info(format(e))
                elif meta_data.type == 'file':
                    self.files[(instance_name, table_name)] = []

                    old_files = []
                    if data != "":
                        old_files = data.split("|")

                    if request.files[key] and util.allowed_file(self.files[key].filename):
                        # http://werkzeug.pocoo.org/docs/0.11/datastructures/#werkzeug.datastructures.FileStorage
                        for filename, file in request.files[key].items():
                            filename = secure_filename(filename)

                            self.files[(instance_name, table_name)].append({'filename': filename, 'file': file})

                            if filename not in old_files:
                                old_files.append(filename)
                    elif request.files[key]:
                        self.instances.set_value(instance_name, field_name, data)
                        errors[new_key] = 'File type not allowed'

                    if len(old_files) > 0:
                        self.instances.set_value(instance_name, field_name, "|".join(old_files))
                else:
                    self.instances.set_value(instance_name, field_name, data)

        return errors

    def save(self):
        commit_status, commit_msg = self.instances.commit()

        if commit_status is True:
            for key in self.files:
                if not self.instances.instance_names[key[1]][key[0]]:
                    continue

                directory = (os.path.join(current_app.config['UPLOAD_FOLDER'], key[1],
                                          self.instances.instance_names[key[1]][key[0]])).strip()

                if not os.path.exists(directory):
                    os.makedirs(directory)

                for file_data in self.files[key]:
                    if os.path.exists(os.path.join(directory, file_data['filename'])):
                        os.remove(os.path.join(directory, file_data['filename']))

                    file_data['file'].save(os.path.join(directory, file_data['filename']))

            current_app.cache.increment_version(list(self.table_names))

        return commit_status, commit_msg

    def undo(self):
        self.instances.rollback()
