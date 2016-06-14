import re
import os
from werkzeug.utils import secure_filename
from iggybase.core.field_collection import FieldCollection
from iggybase.core.data_instance import DataInstance
from iggybase import utilities as util
from flask import request, g, current_app
from collections import OrderedDict


class FormParser():

    def parse(self):
        # fields contain the data that was displayed on the form and possibly edited
        fields = {}
        # data structure containing info about rows saved
        saved_data = OrderedDict()
        table_names = []

        # used to identify fields that contain data that needs to be saved
        field_pattern = re.compile('(data_entry|record_data)_(\S+)_(\d+)')
        for key in request.form:
            data = request.form.get(key)

            # logging.info(key + ': ' + data)

            if key.startswith('bool_'):
                key = key[key.index('_') + 1:]

            field_id = field_pattern.match(key)
            if field_id is not None:
                # logging.info('key: ' + key)
                if field_id.group(3) not in fields.keys():
                    fields[field_id.group(3)] = {'data_entry': {}, 'record_data': {}}

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

        for row_id in sorted(fields.keys()):
            row_data = fields[row_id]

            table_name_field = row_data['record_data']['table_name']
            if table_name_field not in table_names:
                table_names.append(table_name_field)

            instance = DataInstance(row_data['record_data']['table_name'], row_data['record_data']['row_name'])

            if 'organization_id' in row_data['data_entry'].keys():
                row_org_id = row_data['data_entry']['organization_id']
            elif instance.get_value('organization_id') is not None:
                row_org_id = instance.get_value('organization_id')
            elif self.current_org_id is not None:
                row_org_id = g.current_org_id
            else:
                row_org_id = 1

            # convert to an int if numeric
            if row_org_id.isdigit():
                row_org_id = int(row_org_id)

            if not isinstance(row_org_id, int):
                row_orgs = instance.set_foreign_key_field_id({'organization_id': row_org_id})
                row_org_id = row_orgs[0]

            row_data['data_entry']['organization_id'] = row_org_id

            exclude_list = ['id', 'last_modified', 'date_created', 'organization_id']

            # logging.info('for field in current_field_data.items(): ')
            for field, meta_data in instance.fields.items():
                # logging.info('field: ' + field)
                # only update fields that were on the form
                if field not in row_data['data_entry'].keys():
                    continue

                field_data = meta_data.Field

                if 'text' == meta_data.DataType.name.lower and row_data['data_entry'][field] != '':
                    lt = DataInstance('long_text', 'new', instance.get_value(field))

                    lt.set_value('organization_id', row_org_id)
                    lt.set_value('long_text', row_data['data_entry'][field])
                    lt.save()

                    row_data['data_entry'][field] = lt.instance.id
                elif field_data.foreign_key_table_object_id is not None:
                    try:
                        # TODO find a better way to deal with no value in a select
                        # a top row is is added to all selects with an index of -99 (get_foreign_key_data)
                        if int(row_data['data_entry'][field]) == -99:
                            row_data['data_entry'][field] = None
                        else:
                            row_data['data_entry'][field] = int(row_data['data_entry'][field])
                    except ValueError:
                        instance.set_foreign_key_field_id(field, row_data['data_entry'][field])
                elif meta_data.DataType.name.lower() == 'file':
                    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], table_name_field,
                                             instance.instance_name)
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    old_files = []
                    if row_data['old_value'][field] != "":
                        old_files = row_data['old_value'][field].split("|")

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

            instance.set_values(row_data['data_entry'])
            save_msg = instance.save()
            saved_data[save_msg['id']] = save_msg

        current_app.cache.increment_version(list(table_names))

        return saved_data
