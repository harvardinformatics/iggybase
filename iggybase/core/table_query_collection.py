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
            for query in table_queries_info: # page can have multiple
                query = TableQuery(
                    query.TableQuery.id,
                    query.TableQuery.order,
                    query.TableQuery.display_name,
                    None,
                    self.criteria
                )
                queries.append(query)
        elif self.table_name: # use table_name, show all fields, one table_query
            oac = g_helper.get_org_access_control()
            table_object_row = oac.get_row('table_object', {'name': self.table_name})
            query = TableQuery(None, 1,
                    table_object_row.display_name,
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
