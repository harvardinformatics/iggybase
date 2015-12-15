import operator
from flask import request
from iggybase.database import admin_db_session
from iggybase.mod_auth import facility_role_access_control as frac
import iggybase.table_query as tq
import logging

class TableQueryCollection:
    def __init__ (self, module_name, page_form, table_name = None):
        # TODO: make table_name or id optional based on what is in
        # table_query_render
        self.module_name = module_name
        self.module = 'mod_' + self.module_name
        self.table_name = table_name
        self.page_form = page_form
        self.facility_role_access_control = frac.FacilityRoleAccessControl()
        self.results = []

    def get_results(self):
        """ calls several class functions and returns results
        """
        if self.facility_role_access_control.has_access('Module', self.module):
            table_queries_info = self.facility_role_access_control.table_queries(self.page_form, self.table_name)
            for query in table_queries_info:
                order = query.TableQuery.order
                table_query = tq.TableQuery(
                    query.TableQuery.id,
                    order,
                    query.TableQuery.display_name,
                    self.module_name
                )
                table_query.get_results()
                self.results.append(table_query)
            # sort queries by their order
            self.results.sort(key=operator.attrgetter('order'))

    def format_results(self, for_download = False):
        for query in self.results:
            query.format_results(for_download)

    def get_first(self):
        first = []
        if self.results[0]:
            first = self.results[0]
        return first
