from flask import abort
from iggybase import utilities as util
from iggybase import g_helper
from .table_query import TableQuery
import logging

class TableQueryCollection:
    def __init__ (self, table_name = None, criteria = {}):
        self.table_name = table_name
        self.criteria = criteria
        self.rac = g_helper.get_role_access_control()
        self.queries = self._get_queries()

    def get_results(self):
        for query in self.queries:
            query.get_results()

    def _get_queries(self):
        filters = util.get_filters()
        table_queries_info = []
        if not 'all' in filters: # all overrides table_query, shows all fields
            route = util.get_path(2)
            table_queries_info = self.rac.table_queries(route, self.table_name)
        queries = []
        if table_queries_info: # if table_query defined, use id
            first_query = True
            link_tbl_criteria = {}
            for query in table_queries_info: # page can have multiple
                if first_query:
                    first_query = False
                    criteria = self.criteria
                elif self.criteria:
                    for c, val in self.criteria.items():
                        # if there is criteria for row of first table
                        # then add that as id criteria for link tables
                        if c[0] == self.table_name and c[1] == 'name':
                            criteria = {(query.TableQuery.display_name, (self.table_name + '_id')): val}
                query = TableQuery(
                    query.TableQuery.id,
                    query.TableQuery.order,
                    query.TableQuery.display_name,
                    None,
                    criteria
                )
                queries.append(query)
        elif self.table_name: # use table_name, show all fields, one table_query
            table_object_row = self.rac.get_role_row('table_object', {'name': self.table_name})
            if table_object_row:
                if table_object_row.TableObjectRole.display_name:
                    display_name = table_object_row.TableObjectRole.display_name
                else:
                    display_name = table_object_row.TableObject.display_name
            else:
                abort(403)

            query = TableQuery(
                    None,
                    1,
                    display_name,
                    self.table_name,
                    self.criteria)
            queries.append(query)
        return queries

    def format_results(self, add_row_id = True, allow_links = True):
        for query in self.queries:
            query.format_results(add_row_id, allow_links)

    def get_first(self):
        first = None
        if self.queries:
            first = self.queries[0]
        return first
