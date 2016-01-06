import operator
from flask import request
from iggybase.database import admin_db_session
from iggybase.mod_auth import facility_role_access_control as frac
import iggybase.table_query as tq
import logging

class TableQueryCollection:
    def __init__ (self, module_name, page_form, table_name = None):
        self.module_name = module_name
        self.module = 'mod_' + self.module_name
        self.table_name = table_name
        self.page_form = page_form
        self.facility_role_access_control = frac.FacilityRoleAccessControl()
        self.queries = []
        self.results = []

    def get_results(self):
        for query in self.queries:
            query.get_results()
            self.results.append(query)

    def get_fields(self):
        if self.facility_role_access_control.has_access('Module', self.module):
            table_queries_info = self.facility_role_access_control.table_queries(self.page_form, self.table_name)
            if table_queries_info:
                for query in table_queries_info:
                    order = query.TableQuery.order
                    self.populate_query(
                        query.TableQuery.id,
                        order,
                        query.TableQuery.display_name
                    )
            elif self.table_name:
                self.populate_query(None, 1, self.table_name, self.table_name)
            # sort queries by their order
            self.results.sort(key=operator.attrgetter('order'))

    def populate_query(self, id, order, query_name, table_name = None):
        table_query = tq.TableQuery(
            id,
            order,
            query_name,
            self.module_name,
            table_name
        )
        table_query.get_fields()
        self.queries.append(table_query)

    def format_results(self, for_download = False):
        for query in self.results:
            query.format_results(for_download)

    def get_first(self):
        first = []
        if self.queries[0]:
            first = self.queries[0]
        return first
