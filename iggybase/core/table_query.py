from flask import request, g
from collections import OrderedDict
from iggybase import utilities as util
from iggybase import g_helper
from .field_collection import FieldCollection

# Retreives and formats data based on table_query
class TableQuery:
    def __init__ (self, id, order, display_name, table_name = None, criteria = {}):
        self.id = id
        self.order = order
        self.display_name = display_name
        self.table_name = table_name
        self.table_dict = {} # results indexed by row id and table|field name
        self.criteria = criteria
        self.rac = g_helper.get_role_access_control()
        # fields will be decided with id or table_name
        self.fc = FieldCollection(id, table_name)

    def get_results(self):
        """ calls several class functions and returns results
        """
        self.fc.set_fk_fields()
        results = []
        self.criteria = self.add_table_query_criteria(self.criteria)
        joins = []
        if self.id:
            joins = self.get_joins(self.id)
        joins = []
        self.oac = g_helper.get_org_access_control()
        self.results = self.oac.get_table_query_data(
                self.fc.fields,
                self.criteria,
                joins
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
            criteria[criteria_key] = row.TableQueryCriteria.value

        criteria.update(orig_criteria)
        return criteria

    def get_joins(self, id):
        joins = []
        res = self.rac.table_query_table_object(id)
        for tbl in res:
            joins.append(util.get_table(tbl.name))
        return joins

    def format_results(self, add_row_id = True, allow_links = True):
        """Formats data
        - transforms into dictionary
        - adds links
        - calculates calculated fields
        - skips invisible fields, this must be done after data is retreived in
          cases where invisible fields are used in calculations
        """
        if self.results:
            keys = self.results[0].keys()

        # keep track of special fields
        link_fields = {}
        calc_fields = []
        invisible_fields = []
        url_root = request.url_root
        for field in self.fc.fields.values():
            if field.link_visible() and allow_links:
                if field.is_foreign_key:
                    link_fields[field.name] = field.get_link(url_root, 'detail', field.FK_TableObject.name)
                else:
                    link_fields[field.name] = field.get_link(url_root, 'detail', field.TableObject.name)
            if field.is_calculation():
                calc_fields.append(field.name)
            if not field.visible:
                invisible_fields.append(field.name)

        # create dictionary for each row
        for i, row in enumerate(self.results):
            row_dict = OrderedDict()
            for i, col in enumerate(row):
                name = keys[i]

                # set column value
                if name == 'DT_RowId':
                    dt_row_id = col
                    if not add_row_id:
                        continue
                elif name in invisible_fields:
                    continue
                elif name in calc_fields:
                        col = self.fc.fields[name].calculate(col, row,
                                keys)
                elif name in link_fields and col:
                    col_str = str(col)
                    col = ('<a href="' + link_fields[name] + col_str + '">' +
                            col_str + '</a>')
                elif col != None and self.fc.fields[name].type == 'file':
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
                                file = file_split[1]
                        link = self.fc.fields[name].get_file_link(url_root, row_name, file)
                        file_links.append('<a href="' + link + '" target="_blank">' + file + '</a>')
                    col = '|'.join(file_links)
                elif (col != None
                        and (self.fc.fields[name].type == 'decimal'
                            or self.fc.fields[name].type == 'float')
                ):
                    col = int(col)
                row_dict[name] = col
            if row_dict:
                # store values as a dict of dict so we can access any of the
                # data by row_id and field display_name
                if dt_row_id in self.table_dict:
                    dt_row_id += 99
                self.table_dict[dt_row_id] = row_dict

    def get_list_of_list(self): # for download
        table_list = []
        keys = []
        for key in self.get_first().keys():
            keys.append(self.get_display_name(key))
        table_list.append(keys)
        for row in self.table_dict.values():
            table_list.append(list(row.values()))
        return table_list

    def get_first(self): # for detail
        return self.get_row_list()[0]

    def get_row_list(self): # for summary_ajax
        return list(self.table_dict.values())

    def update_and_get_message(self, updates, ids, message_fields):
        updated = self.oac.update_rows(self.display_name, updates, ids)
        updated_info = []
        for i in updated:
            # for each row grab any message_fields, to inform the user about the
            # update
            row_fields = []
            for field in message_fields:
                val = self.table_dict[i][field]
                if val:
                    row_fields.append(str(val))
            if row_fields:
                updated_info.append(', '.join(row_fields))
            else:
                updated_info.append('no ' + ', '.join(message_fields) + ' for id = ' + str(i))
        return updated_info

    def get_display_name(self, name):
        # get field obj display name from table_name|field_name
        return self.fc.fields[name].display_name
