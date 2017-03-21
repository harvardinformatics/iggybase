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
        self.oac = g_helper.get_org_access_control()
        self.queries = self._get_queries()

    def get_results(self, allow_links = True):
        for query in self.queries:
            query.get_results(allow_links)

    def _get_queries(self):
        filters = util.get_filters()
        table_queries_info = []
        if not 'all' in filters: # all overrides table_query, shows all fields
            route = util.get_path(2)
            table_queries_info = self.rac.table_queries(route, self.table_name)
        queries = []
        if table_queries_info: # if table_query defined, use id
            query_cnt = len(table_queries_info)
            for i, query in enumerate(table_queries_info): # page can have multiple
                criteria = self.criteria
                if (i + 1) < query_cnt: # if there are more queries
                    # set criteria for next query based on rows of this query
                    self.criteria = self.row_criteria(query)
                query = TableQuery(
                    query.TableQuery.id,
                    query.TableQuery.order,
                    query.TableQuery.display_name,
                    None,
                    criteria,
                    query.TableQueryRender.description,

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

    def row_criteria(self, tq):
        # link val will be the name of current table, following queries must
        # include that column to work
        link_table = tq.TableQuery.link_table
        criteria = {}
        # check criteria, link val might be passed in
        for c, val in self.criteria.items():
            if c[0] == link_table and c[1] == 'name':
                criteria = {(link_table, 'name'): val}
                break;
        # if no link val was found then query for them
        if not criteria:
            tbls = [link_table]
            for c, val in self.criteria.items():
                tbls.append(c[0])
            rows = self.oac.get_row_multi_tbl(tbls, self.criteria, [], False,
                    False, [link_table])
            names = []
            for row in rows:
                names.append(row.name)
            criteria = {(link_table, 'name'): names}
        return criteria

    def format_results(self, add_row_id = True, allow_links = True):
        for query in self.queries:
            query.format_results(add_row_id, allow_links)

    def get_first(self):
        first = None
        if self.queries:
            first = self.queries[0]
        return first
