from flask import request, g
import time
from collections import OrderedDict
from iggybase import utilities as util
from iggybase import g_helper
from .field_collection import FieldCollection

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, id, order, display_name, table_name = None, criteria = {}, description = ''):
        self.id = id
        self.order = order
        self.display_name = (display_name or table_name).replace('_', ' ')
        self.table_name = table_name
        self.table_dict = OrderedDict() # results indexed by row id and table|field name
        self.criteria = criteria
        self.description = description
        self.rac = g_helper.get_role_access_control()
        # fields will be decided with id or table_name
        self.fc = FieldCollection(id, table_name)

    def get_results(self, allow_links):
        """ calls several class functions and returns results
        """
        start = time.time()
        # TODO: set_fk_fields is slow
        self.fc.set_fk_fields()
        current = time.time()
        print('set fk: ' + str(current - start))
        results = []
        self.criteria = self.add_table_query_criteria(self.criteria)
        current = time.time()
        print('crit: ' + str(current - start))
        self.oac = g_helper.get_org_access_control()
        current = time.time()
        print('before table query data: ' + str(current - start))
        self.results = self.oac.get_table_query_data(
                self.fc,
                self.criteria,
                allow_links
        )
        return self.results

    def add_table_query_criteria(self, orig_criteria):
        criteria = {}
        # add criteria from get params
        filters = util.get_filters()
        for key, val in filters.items():
            if key in self.fc.fields:
                field = self.fc.fields[key]
                criteria_key = (field.TableObject.name, field.Field.display_name)
                criteria[criteria_key] = val
        # add criteria from db
        res = self.rac.table_query_criteria(
            self.id
        )
        for row in res:
            criteria_key = (row.TableObject.name, row.Field.display_name)
            if row.TableQueryCriteria.comparator != None:
                criteria[criteria_key] = {
                        'compare': row.TableQueryCriteria.comparator,
                        'value': row.TableQueryCriteria.value
                }
            else:
                criteria[criteria_key] = row.TableQueryCriteria.value
        criteria.update(orig_criteria)
        return criteria

    def format_results(self, add_row_id = True, allow_links = True):
        """Formats data
        only loops through rows if
        - calculates calculated fields
        - file fields which need to be made into links
        TODO: there might be a bug to fix here since invisible fields that might
        be in calculations will not be in the select from get_table_query_data
        """
        if self.results:
            keys = self.results[0].keys()
        # keep track of special fields
        calc_fields = []
        file_fields = []
        invisible_fields = []
        url_root = request.url_root
        for field in self.fc.fields.values():
            if field.is_calculation():
                calc_fields.append(field.name)
            if not field.visible:
                invisible_fields.append(field.name)
            if field.type == 'file':
                file_fields.append(field.name)
        # create dictionary for each row
        if calc_fields or file_fields:
            row_list = []
            for i, row in enumerate(self.results):
                row_formatted = []
                if row:
                    dt_row_id = row[len(row)-1]
                else:
                    dt_row_id = None
                for i, col in enumerate(row):
                    name = keys[i]
                    if name in invisible_fields:
                        continue
                    elif name in calc_fields:
                            col = self.fc.fields[name].calculate(col, row,
                                    keys)
                    elif name in file_fields and col != None:
                        filelist = col.split('|')
                        file_links = []
                        row_name = None
                        for file in filelist:
                            if not row_name:
                                # row_name is being selected like:
                                # rowname/one,two,three
                                # it will only show up in the split of the first
                                # file but should be used for all
                                file_split = file.split('/')
                                if len(file_split) > 1:
                                    row_name = file_split[0]
                                    file = ('/').join(file_split[1:])
                            link = self.fc.fields[name].get_file_link(url_root, row_name, file)
                            file_links.append('<a href="' + link + '" target="_blank">' + file + '</a>')
                        col = '|'.join(file_links)
                    row_formatted.append(col)
                if row_formatted:
                    row_list.append(row_formatted)
            self.results = row_list
        return self.results

    def get_first_row_dict(self):
        row_dict = OrderedDict()
        row = self.get_first()
        # using index because formatted results are list and unformatted results
        # are a sqlalchemy object and both contian only visible fields and need
        # to pull the display name from fields dict
        i = 0
        for key, field in self.fc.fields.items():
            if field.visible:
                row_dict[field.display_name] = row[i]
                i += 1 # only visible values will be in results
        return row_dict

    def get_first(self): # for detail
        return self.results[0]

    # TODO: this will be broken, fix
    def update_and_get_message(self, table_name, updates, ids, message_fields,
            tbl_ids):
        updated_info = set([])
        for tbl, col_updates in updates.items():
            updated = self.oac.update_rows(tbl, col_updates, ids[(tbl, 'id')])
            for i in updated:
                row_ids = tbl_ids[(tbl, 'id')]
                row_ids = row_ids[str(i)]
                for row_id in row_ids:
                    # for each row grab any message_fields, to inform the user about the
                    # update
                    row_fields = []
                    for field in message_fields:
                        val = self.table_dict[row_id][field]
                        if val:
                            row_fields.append(str(val))
                    if row_fields:
                        updated_info.add(', '.join(row_fields))
                    else:
                        updated_info.add('no ' + ', '.join(message_fields) + ' for id = ' + i)
        return list(updated_info)

    def get_display_name(self, name):
        # get field obj display name from table_name|field_name
        return self.fc.fields[name].display_name
