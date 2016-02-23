import operator
from iggybase.mod_auth import role_access_control as rac
from .utilities import get_filters
from .table_query import TableQuery
import logging

class TableQueryCollection:
    def __init__ (self, facility_name, page_form, table_name = None, criteria = {}):
        self.facility_name = facility_name
        self.table_name = table_name
        self.page_form = page_form
        self.criteria = criteria
        self.role_access_control = rac.RoleAccessControl()
        self.queries = []
        self.results = []

    def get_results(self):
        for query in self.queries:
            query.get_results()
            self.results.append(query)

    def get_fields(self):
        filters = get_filters()
        table_queries_info = []
        if not 'all' in filters:
            table_queries_info = self.role_access_control.table_queries(self.page_form, self.table_name)

        if table_queries_info:
            for query in table_queries_info:
                order = query.TableQuery.order
                # TODO: constant for pages that need row_id?
                row_id = (self.page_form in ['action_summary', 'update'])
                self.populate_query(
                    query.TableQuery.id,
                    order,
                    query.TableQuery.display_name,
                    None,
                    self.criteria,
                    row_id
                )
        elif self.table_name:
            self.populate_query(None, 1, self.table_name, self.table_name,
                    self.criteria)
        # sort queries by their order
        self.results.sort(key=operator.attrgetter('order'))

    def populate_query(self, id, order, query_name, table_name = None, criteria
            = {}, row_id = False):
        tq = TableQuery(
            id,
            order,
            query_name,
            self.facility_name,
            table_name,
            criteria,
            row_id
        )
        tq.get_fields()
        self.queries.append(tq)

    def format_results(self, for_download = False):
        for query in self.results:
            query.format_results(for_download)

    def get_first(self):
        first = []
        if self.queries:
            first = self.queries[0]
        return first
