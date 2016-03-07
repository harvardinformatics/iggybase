import operator
from iggybase import utilities as util
from .table_query import TableQuery
import logging

class TableQueryCollection:
    def __init__ (self, page_form, table_name = None, criteria = {}):
        self.table_name = table_name
        self.page_form = page_form
        self.criteria = criteria
        self.role_access_control = util.get_role_access_control()
        self.queries = self._get_queries()

    def get_results(self):
        for query in self.queries:
            query.get_results()

    def _get_queries(self):
        filters = util.get_filters()
        table_queries_info = []
        if not 'all' in filters:
            table_queries_info = self.role_access_control.table_queries(self.page_form, self.table_name)
        queries = []
        if table_queries_info:
            for query in table_queries_info:
                query = TableQuery(
                    query.TableQuery.id,
                    query.TableQuery.order,
                    query.TableQuery.display_name,
                    None,
                    self.criteria
                )
                queries.append(query)
        elif self.table_name:
            query = TableQuery(None, 1, self.table_name, self.table_name,
                    self.criteria)
            queries.append(query)
        return queries

    def format_results(self, add_row_id = True, allow_links = True):
        for query in self.queries:
            query.format_results(add_row_id, allow_links)

    def get_first(self):
        first = []
        if self.queries:
            first = self.queries[0]
        return first
