from flask import g, current_app, session
from sqlalchemy import DateTime, func, cast, String, desc, or_
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError, NoForeignKeysError, IdentifierError, \
    NoReferenceError
from iggybase.database import db_session
from iggybase.admin import models
from iggybase import utilities as util
from sqlalchemy.orm import aliased, defer
from sqlalchemy.dialects import mysql
import json
import logging
import time

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__(self):
        self.current_org_id = None
        self.session = self.get_session()
        self.org_ids = self.get_default_org_ids()

        if (g.user is not None and not g.user.is_anonymous):
            self.set_user(g.user.id)
        else:
            self.user = None

    def set_user(self, user_id):
        self.user =  self.session.query(models.User).filter_by(id=user_id).first()
        # must distinguish user level orgs from group level org ids
        query = self.session.query(models.Organization.parent_id.distinct().label('parent_id'))
        self.parent_orgs = [row.parent_id for row in query.all()]
        facility_root_org_id = session['root_org_id']

        user_orgs = self.session.query(models.UserOrganization).filter_by(active=1, user_id=self.user.id).all()

        facility_orgs = {}
        for user_org in user_orgs:
            if user_org.user_organization_id is not None:
                level = self.get_facility_orgs(user_org.user_organization_id, facility_root_org_id, 0)
                if level is not None:
                    facility_orgs[user_org.user_organization_id] = level

        filters = util.get_filters()
        if 'set_orgs' not in filters and 'org_id' in session and session['org_id']:
            self.current_org_id = session['org_id']['current_org_id']
            self.org_ids.extend(session['org_id']['org_ids'])
            print('in session')
        else:
            print('not in session')
            self.current_org_id = None
            self.org_ids = self.get_default_org_ids()
            min_level = None
            for user_org, level in facility_orgs.items():
                # levels are ordered from high to low, hightest has order = 1
                if min_level is None or (level < min_level and user_org != self.user.organization_id):
                    # TODO: do we really want min level.id or do we want the lowest
                    # level.order
                    min_level = level
                    self.current_org_id = user_org
                self.get_child_organization(user_org)
            session['org_id'] = {'current_org_id': self.current_org_id, 'org_ids': self.org_ids}
        return (self.org_ids != [])

    def __del__ (self):
        self.session.rollback()

    def get_session(self):
        session = db_session()

        return session

    def commit(self):

        try:
            self.session.commit()
            return True, None
        except (IntegrityError, DataError, SQLAlchemyError, NoForeignKeysError, IdentifierError, NoReferenceError) as e:
            self.session.rollback()
            logging.error("Commit Error: " + format(e))
            return False, "Commit Error: " + format(e)

    def flush(self):
        try:
            self.session.flush()
            return True, None
        except (IntegrityError, DataError, SQLAlchemyError, NoForeignKeysError, IdentifierError, NoReferenceError) as e:
            self.session.rollback()
            logging.error("Flush Error: " + format(e))
            return False, "Flush Error: " + format(e)

    def fields(self, table_object_id, filter=None, active=1):
        filters = [
            (models.FieldRole.role_id == self.role.id),
            (models.Field.table_object_id == table_object_id),
            (models.Field.active == active),
            (models.FieldRole.active == active)
        ]

        if filter is not None:
            for display_name, value in filter.items():
                field_data = display_name.split(".")

                if field_data[0] == "field":
                    filters.append((getattr(models.Field, field_data[1]) == value))
                else:
                    filters.append((getattr(models.FieldRole, field_data[1]) == value))

        res = (self.session.query(models.Field, models.FieldRole, models.DataType).
               join(models.FieldRole).
               join(models.DataType).
               filter(*filters).
               order_by(models.FieldRole.order, models.FieldRole.display_name).all())


        if res is None:
            return {'Field': {}, 'FieldRole': {}, 'DataType': {}}
        else:
            return res


    def rollback(self):
        self.session.rollback()

    def get_default_org_ids(self):
        filters = [
                models.Organization.name == 'Everyone',
                models.Organization.active == 1
        ]
        everyone = self.session.query(models.Organization).filter(*filters).first()
        if everyone:
            return [everyone.id]
        else:
            return []

    def get_facility_orgs(self, org_id, root_org_id, level):
        level += 1

        if org_id == root_org_id:
            return level

        root_org = self.session.query(models.Organization).filter_by(id=org_id).first()
        if root_org is None:
            return None
        elif root_org.parent_id is None:
            return None
        else:
            return self.get_facility_orgs(root_org.parent_id, root_org_id, level)

    def get_child_organization(self, parent_organization_id):
        self.org_ids.append(parent_organization_id)
        # logging.info('child_org: ' + str(parent_organization_id))
        child_orgs = self.session.query(models.Organization).filter_by(parent_id=parent_organization_id).all()
        for child_org in child_orgs:
            if child_org.id in self.parent_orgs:
                self.get_child_organization(child_org.id)
            else:
                self.org_ids.append(child_org.id)
        return

    def get_query_count(self, query):
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = self.session.execute(count_q).scalar()
        return count

    def get_instance_data(self, table_object, criteria):
        filters = [getattr(table_object, 'organization_id').in_(self.org_ids)]

        if 'name' in criteria and (criteria['name'] == ['new'] or criteria['name'] == ['empty_row']):
            instance = table_object()
            instance.name = criteria['name'][0]
            return [instance]

        for field, value in criteria.items():
            filters.append(getattr(table_object, field).in_(value))

        qry = self.session.query(table_object).filter(*filters)
        qry_count = self.get_query_count(qry)

        if qry_count == 0:
            return [table_object()]
        else:
            res = qry.all()
            return res

    def get_select_list(self, select_list_id, active=1):
        select_list_items = self.get_select_list_items_from_id(select_list_id)

        results = [(-99, '')]

        for row in select_list_items:
            results.append((row.id, row.display_name))

        return results

    def get_select_list_items_from_id(self, select_list_id, criteria = [], active=1):
        select_list_items = (self.session.query(models.SelectListItem)
            .filter_by(select_list_id=select_list_id)
            .filter_by(active=active)
            .filter(*criteria).all())
        return select_list_items

    def get_select_list_item(self, table, field, item, active=1):
        # TODO: using display_name here means we need to use display_name in
        # the table query or make adjustments here
        filters = [
                (models.TableObject.name == table),
                (models.Field.display_name == field),
                (models.Field.active == active),
                (models.TableObject.active == active)
                ]
        field_row = (self.session.query(models.Field)
                .join(models.TableObject, models.TableObject.id ==
                    models.Field.table_object_id)
                .filter(*filters).first())
        select_list_id = getattr(field_row, 'select_list_id', None)
        criteria = [(models.SelectListItem.display_name == item)]
        select_list_items = self.get_select_list_items_from_id(select_list_id,
                criteria)
        item = None
        if select_list_items:
            item = select_list_items[0]
        return item

    def get_foreign_key_data(self, fk_table_data, fk_field_data, params=None):
        # logging.info(fk_table_data)
        # logging.info(fk_field_data)
        results = [(-99, '')]
        if fk_field_data is not None:
            fk_table_object = util.get_table(fk_table_data.name)
            filters = [
                getattr(fk_table_object, 'organization_id').in_(self.org_ids),
                getattr(fk_table_object, 'active') == 1
            ]
            if params is None:
                rows = self.session.query(getattr(fk_table_object, 'id'), getattr(fk_table_object, fk_field_data.display_name).label('name')).filter(*filters).order_by('order').all()
            else:
                for key, value in params.items():
                    filters.append(getattr(fk_table_object, key) == value)

                rows = self.session.query(getattr(fk_table_object, 'id'),
                                          getattr(fk_table_object,
                                                  fk_field_data['foreign_key'])).filter(*filters).order_by('order').all()
            for row in rows:
                results.append((row.id, row.name))
        return results

    def get_table_query_data(self, fc, criteria={}, active = 1):
        # TODO: consider factoring out part of this or something to make this
        # easier to digest
        results = []
        tables = []
        joins = []
        table_models = {}
        outer_joins = []
        columns = []
        fk_columns = []
        aliases = {}
        wheres = []
        group_by = []
        order_by = {}
        first_table_named = None  # set to first table name, dont add to joins
        for key, field in fc.fields.items():
            join_type = None # set to outer or inner
            # Get the table to display, fk table for fks
            if field.is_foreign_key:
                table_name = field.FK_TableObject.name
            else:
                table_name = field.TableObject.name
            if table_name in table_models:
                table_model = table_models[table_name]
            else:
                table_model = util.get_table(table_name)
                table_models[table_name] = table_model

            # handle fks
            if field.is_foreign_key:
                if field.TableObject.name in table_models:
                    fk_table_model = table_models[field.TableObject.name]
                else:
                    fk_table_model = util.get_table(field.TableObject.name)
                    table_models[field.TableObject.name] = fk_table_model
                # create alias to the fk table
                # solves the case of more than one join to same table
                alias_name = field.TableObject.name + '_' + field.Field.display_name + '_' + field.FK_TableObject.name + '_' + field.FK_Field.display_name
                # possible to have two of the same field with calculations
                if alias_name not in aliases:
                    aliases[alias_name] = aliased(table_model, name = alias_name)
                    outer_joins.append((
                        aliases[alias_name],
                        getattr(fk_table_model, field.Field.display_name) == aliases[alias_name].id
                    ))
                    join_type = 'outer'
                col = getattr(aliases[alias_name],
                    field.FK_Field.display_name)

            else:  # non-fk field
                col = getattr(table_model, field.Field.display_name)
                if field.type == 'file': # give name as well
                    col = getattr(table_model, 'name') + '/' + col

                # add to joins if not first table, avoid joining to self
                if (not first_table_named
                    or (first_table_named == field.TableObject.name)):
                    first_table_named = field.TableObject.name
                    if table_model not in tables:
                        tables.append(table_model)
                    join_type = 'inner'
                else:
                    if field.group_func:
                        outer_joins.append(table_model)
                        join_type = 'outer'
                    elif table_model not in joins:
                        joins.append(table_model)
                        if table_model not in tables:
                            tables.append(table_model)
                        join_type = 'inner'

            if field.group_by == 1:
                group_by.append(col)
            if field.group_func:
                col = func.ifnull((getattr(func, field.group_func)(col.op('SEPARATOR')(', '))), '')
            columns.append(col.label(field.name))
            # set order by to first column asc if not set
            if not order_by:
                if fc.order_by:
                    order_by = fc.order_by
                elif field.visible:
                    order_by = {key:{'desc':False}}

            criteria_key = (field.TableObject.name, field.Field.display_name)
            # don't include criteria for self foreign keys
            if criteria_key in criteria and not (field.is_foreign_key and
                field.FK_TableObject.name == first_table_named):
                if type(criteria[criteria_key]) is list:
                    crit_where = [(col.in_(criteria[criteria_key]))]
                    include_nulls = False
                elif type(criteria[criteria_key]) is dict:
                    include_nulls, crit_where = self.criteria_dict(col, criteria[criteria_key])
                else:
                    crit_where = [col == criteria[criteria_key]]
                    include_nulls = False
                # if outer join criteria then must include nulls
                # TODO: possible to add criteria to table join - first try at
                # this failed since we are using natural joins
                if include_nulls and join_type == 'outer':
                    for i, c in enumerate(crit_where):
                        crit_where[i] = (or_(col == None, c))
                # add any criteria to the where
                wheres.extend(crit_where)
        id_cols = []
        # add organization id checks on all tables, does not include fk tables,
        # or outer join tables
        for table_model in tables:
            # add a row id that is the id of the first table named
            id_table_name = table_model.__table__.name.lower()
            id_table_col = getattr(table_model, 'id')
            id_cols.append(id_table_name + '-' + cast(id_table_col, String))
            # user row has one org_id but user_orgs are many
            if id_table_name == 'user':
                wheres.append(or_(
                    getattr(table_model, 'organization_id').in_(self.org_ids),
                    getattr(table_model, 'id') == g.user.id
                ))
            else:
                wheres.append(getattr(table_model, 'organization_id').in_(self.org_ids))
            wheres.append(getattr(table_model, 'active') == active)
        first = True
        for c in id_cols:
            if first:
                id_col = c
                first = False
            else:
                id_col = id_col.concat('|' + c)
        # format order_by
        order_by_list = self.format_order_by(order_by)
        columns.append(id_col.label('DT_RowId'))
        start = time.time()

        stmt = self.session.query(*columns). \
                join(*joins). \
                outerjoin(*outer_joins). \
                filter(*wheres).group_by(*group_by).order_by(*order_by_list)

        # query = stmt.statement.compile(dialect=mysql.dialect())
        # logging.info('query')
        # logging.info(str(query))
        # logging.info(str(query.params))

        results = (stmt.all())

        print('query: ' + str(time.time() - start))
        return results

    def criteria_dict(self, col, criteria):
        wheres = []
        include_nulls = False
        if ('from' in criteria and 'to' in criteria):
            wheres = [(col >= criteria['from']),
                      (col < criteria['to'])]
        if( 'compare' in criteria and 'value' in criteria):
            if criteria['compare'] == 'greater than':
                wheres = [(col > criteria['value'])]
            elif criteria['compare'] == 'greater than equal':
                wheres = [(col >= criteria['value'])]
            elif criteria['compare'] == 'less than':
                wheres = [(col < criteria['value'])]
            elif criteria['compare'] == 'less than equal':
                wheres = [(col <= criteria['value'])]
            elif criteria['compare'] == '!=':
                wheres = [col != criteria['value']]
                include_nulls = True
        return include_nulls, wheres

    def format_order_by(self, order_by):
        order_by_list = []
        for key, val in order_by.items():
            if val['desc']:
                order_by_list.append(desc(key))
            else:
                order_by_list.append(key)
        return order_by_list

    def foreign_key(self, table_object_id, display = None):
        filters = [(models.Field.table_object_id == table_object_id)]
        if not display:
            # name is default display column for FK
            filters.append(models.Field.display_name == 'name')
        else:
            filters.append(models.Field.id == display)
        res = (self.session.query(models.Field, models.TableObject).
               join(models.TableObject, models.TableObject.id == models.Field.table_object_id).
               join(models.TableObjectRole, models.TableObject.id == models.TableObjectRole.table_object_id).
               filter(*filters).first())
        return {'foreign_key': res.Field.display_name,
                'name': res.TableObject.name
                }

    def get_search_results(self, table_name, params):
        table = util.get_table(table_name)
        filters = []
        for key, value in params.items():
            filters.append((getattr(table, key)).like('%' + value + '%'))

        # only return organizations the user belongs to
        if table_name == 'Organization':
            filters.append((getattr(table, 'id')).in_(self.org_ids))
        else:
            filters.append((getattr(table, 'organization_id')).in_(self.org_ids))

        return table.query.filter(*filters).order_by(getattr(table, 'name'))

    def get_long_text(self, lt_id, table=None):
        if table is None:
            table = util.get_table("long_text")

        return table.query.filter_by(id=lt_id).first()

    def save_data_instance(self, update_instances, new_instances, background_instances=[]):
        # actions = self.get_table_object_actions()
        # TODO: remove this and replace with actions
        # actions may want to be done after the commit which will require change
        # to insert_row, we can do that as needed
        # for instance in (new_instances + update_instances):
            # if (instance.__tablename__ == 'test_smms' and instance.status_id == 34):
            #     params = '{["test_smms"], "parent":"line_item"}'
                # func = getattr(bill, 'insert_line_item', None)
                # if func:
                #     func(instance)

        self.session.add_all(new_instances + update_instances + background_instances)

        flush_status, flush_err = self.flush()

        if flush_status:
            inst_data = {}
            for instance in (new_instances + update_instances):
                inst_data[instance.id] = {'id': instance.id, 'name': instance.name, 'table': instance.__tablename__}

            commit_status, commit_err = self.commit()
            if commit_status is True:
                return True, inst_data
            else:
                self.rollback()
                return False, commit_err
        else:
            self.rollback()
            return flush_status, flush_err

    def get_row_id(self, table_name, params):
        result = self.get_row(table_name, params)
        if result:
            return result.id
        else:
            return None

    def get_row_multi_tbl(self, table_names, params, order_by = [], first_row = False, org_filter = False, select_tbls = None):
        criteria = []
        joins = []
        selects = []
        tbl_objs = {}
        for tbl in table_names:
            table_object = util.get_table(tbl)
            tbl_objs[tbl] = table_object
            if selects: # join tables after first
                joins.append(table_object)
            # always select first query, if select_tbls is set then only select
            # tables in the list
            if not selects or not select_tbls or tbl in select_tbls:
                selects.append(table_object)
            if org_filter:
                criteria.append(getattr(table_object, 'organization_id') == self.current_org_id)
        for key, val in params.items():
            if key[0] in tbl_objs:
                col = getattr(tbl_objs[key[0]], key[1])
                if isinstance(val, dict):
                    include_nulls, crit_where = self.criteria_dict(col, val)
                    criteria.extend(crit_where)
                elif isinstance(val, list):
                    criteria.append(col.in_(val))
                else:
                    criteria.append(col == val)
        if first_row:
            result = self.session.query(*selects).join(*joins).filter(*criteria).order_by(*order_by).first()
        else:
            result = self.session.query(*selects).join(*joins).filter(*criteria).order_by(*order_by).all()
        return result

    def get_row(self, table_name, params, first = True, org_filter = False):
        table_object = util.get_table(table_name)

        criteria = []

        for key, value in params.items():
            criteria.append(getattr(table_object, key) == value)
        if org_filter:
            criteria.append(getattr(table_object, 'organization_id') == self.current_org_id)
        if first:
            result = self.session.query(table_object).filter(*criteria).first()
        else:
            result = self.session.query(table_object).filter(*criteria).all()

        return result

    def get_price(self, criteria):
        result = None
        org_row = self.get_row('organization', {'id': self.current_org_id})
        org_type_id = getattr(org_row, 'organization_type_id')
        if org_type_id:
            where = []
            table_object = util.get_table('price_list')
            where.append(getattr(table_object, 'price_item_id') == criteria['price_item_id'])
            where.append(getattr(table_object, 'organization_type_id') ==
                    org_type_id)
            result = self.session.query(table_object).filter(*where).first()
        return result

    def get_table_object(self, criteria={}):
        table_object = util.get_table('table_object')

        filters = []
        for key, value in criteria.items():
            filters.append(getattr(table_object, key) == value)

        result = self.session.query(table_object).filter(*filters).first()

        return result

    def get_descendant_data(self, child_table_name, child_link_field_id, parent_ids):
        field = self.session.query(models.Field).filter_by(id=child_link_field_id).first()

        child_table = util.get_table(child_table_name)
        parent_column = getattr(child_table, field.display_name)

        filters = [getattr(child_table, 'organization_id').in_(self.org_ids), parent_column.in_(parent_ids)]

        # logging.info('child_table_name: ' + child_table_name)
        # logging.info('parent_column.name: ' + parent_column.name)

        rows = self.session.query(child_table).\
            filter(*filters).order_by('order', 'name').all()

        row_data = []
        for index, row in enumerate(rows):
            row_data.append({'parent_id': getattr(row, field.display_name), 'instance': row})

        return row_data

    def update_obj_rows(self, items, updates):
        updated = []
        for item in items:
            row_updates = []
            tbls_updated = []
            for field, val in updates.items():
                try:
                    setattr(item, field, val)
                    row_updates.append(item.__tablename__ + '|' + field)
                    tbls_updated.append(item.__tablename__)
                except AttributeError:
                    print('failed to update')
            # commit if we were able to all updates for the row
            if len(updates) == len(row_updates):
                self.session.commit()
                updated.append(item.id)
                # change table version in cache
                for tbl in tbls_updated:
                    current_app.cache.increment_version([tbl])
            else:
                self.session.rollback()
                print('rollback')
        return updated

    def update_rows(self, table, updates, ids):
        ids.sort()
        table_model = util.get_table(table)

        filters = [
                table_model.id.in_(ids),
                getattr(table_model, 'organization_id').in_(self.org_ids)
        ]
        rows = table_model.query.filter(*filters).order_by('id').all()

        updated = []
        for i, row in enumerate(rows):
            row_updates = []
            for col, val in updates.items():
                try:
                    col_obj = getattr(table_model, col)
                    if isinstance(col_obj.type, DateTime) and val == 'now':
                        val = func.now()
                    setattr(row, col, val)
                    row_updates.append(col)
                except AttributeError:
                    print('failed to update')
            # commit if we were able to make all updates for the row
            if len(updates) == len(row_updates):
                self.session.commit()
                updated.append(ids[i])
                # change table version in cache
                current_app.cache.increment_version([table])
            else:
                self.session.rollback()
                print('rollback')
        return updated

    def set_work_items(self, work_item_group_id, save_items, parent, work_items = None):
        table_model = util.get_table('work_item')
        work_item_table_object = self.session.query(models.TableObject).filter_by(name='work_item').first()
        table_object_id = None
        success = False
        parent_work_item_id = None
        try:
            for item in save_items:
                table_object = self.session.query(models.TableObject).filter_by(name=item['table']).first()
                # if table extends then set to the base table
                table_object_id = (
                        table_object.extends_table_object_id or table_object.id
                )
                old_item_exists = None
                if work_items:
                    # see if item already saved
                    for old_item in work_items:
                        if old_item.WorkItem.table_object_id == table_object_id and old_item.WorkItem.row_id == item['id']:
                            old_item_exists = old_item
                            break # break loop because we found it
                            continue # skip to next saved_item

                # if we didn't find an old one then insert a new row
                new_name = work_item_table_object.get_new_name()
                if parent:
                    parent_table_object_id = self.session.query(models.TableObject.id).filter_by(name=parent['table']).first()[0]
                    filters = [
                            (models.WorkItem.work_item_group_id == work_item_group_id),
                            (models.WorkItem.table_object_id ==
                                parent_table_object_id),
                            (models.WorkItem.row_id == parent['id'])

                    ]
                    parent_work_item_id = self.session.query(models.WorkItem.id).filter(*filters).first()[0]
                new_row = table_model(name = new_name, active = 1,
                        organization_id = self.current_org_id, work_item_group_id = work_item_group_id,
                        table_object_id = table_object_id, row_id = item['id'],
                        parent_id = parent_work_item_id)
                self.session.add(new_row)
        except:
            self.session.rollback()
            print('rollback')
            logging.info(
                'save_work_item rollback- params: '
                + ' work_item_group_id: ' + str(work_item_group_id)
                + ' parent: ' + str(parent)
                + ' save_items: ' + json.dumps(save_items)
            )
        else:
            print('commit')
            self.session.commit()
            success = True
        return success

    def get_step_actions(self, step_id, timing, active = 1):
        return (self.session.query(models.Action, models.ActionStep, models.SelectListItem,
                                   models.ActionEmail)
                .join(models.ActionStep,  models.Action.id == models.ActionStep.action_id)
                .join(models.SelectListItem,  models.SelectListItem.id == models.ActionStep.timing)
                .outerjoin(models.ActionEmail, models.ActionEmail.id == models.Action.id)
                .filter(
                    models.ActionStep.step_id==step_id,
                    models.ActionStep.active==active,
                    models.Action.active==active,
                    models.SelectListItem.display_name == timing
                ).order_by(models.ActionStep.order).all())

    def get_table_object_actions(self, table_object_id, event_id, active = 1):
        return (self.session.query(models.Action, models.ActionTableObject, models.SelectListItem,
                                   models.ActionEmail, models.Field)
                .join(models.ActionTableObject,  models.Action.id == models.ActionTableObject.action_id)
                .join(models.SelectListItem,  models.SelectListItem.id == models.ActionTableObject.event_id)
                .outerjoin(models.ActionEmail, models.ActionEmail.id == models.Action.id)
                .outerjoin(models.Field, models.Field.id == models.ActionTableObject.field_id)
                .filter(
                    models.ActionTableObject.table_object_id==table_object_id,
                    models.ActionTableObject.active==active,
                    models.Action.active==active,
                    models.SelectListItem.display_name == event_id
                ).order_by(models.ActionTableObject.order).all())

    def get_action(self, action_id, active = 1):
        return (self.session.query(models.Action, models.ActionEmail)
                .outerjoin(models.ActionEmail, models.ActionEmail.id == models.Action.id)
                .filter(
                    models.Action.active==active,
                    models.Active.id == action_id
                ).order_by(models.Action.order).all())

    def get_attr_from_id(self, table_object_id, row_id, attr):
        table_object = self.session.query(models.TableObject).filter_by(id=table_object_id).first()
        table_model = util.get_table(table_object.name)
        row = self.session.query(table_model).filter_by(id=row_id).first()
        return getattr(row, attr)

    def work_item_group(self, work_item_group):
        res = None
        if work_item_group:
            res = (self.session.query(models.WorkItemGroup).
                filter(models.WorkItemGroup.name == work_item_group,
                    models.WorkItemGroup.organization_id.in_(self.org_ids)).first())
        return res

    def work_items(self, work_item_group_id):
        res = None
        if work_item_group_id:
            res = (self.session.query(models.WorkItem, models.TableObject)
                    .join(models.TableObject, models.WorkItem.table_object_id ==
                        models.TableObject.id).
                filter(models.WorkItem.work_item_group_id == work_item_group_id, models.WorkItem.organization_id.in_(self.org_ids)).all())
        return res

    def insert_row(self, table, fields = {}):
        new_row = None
        table_model = util.get_table(table)
        table_table_object = self.session.query(models.TableObject).filter_by(name=table).first()
        # if table is extended get base table to provide new_name
        if table_table_object.extends_table_object_id:
            table_table_object = (self.session.query(models.TableObject)
                    .filter_by(id=table_table_object.extends_table_object_id).first())

        # ensure one inserts under ones current_org_id
        fields['organization_id'] = self.current_org_id
        try:
            fields['name'] = table_table_object.get_new_name()
            new_row = table_model(**fields)
            self.session.add(new_row)
        except:
            self.session.rollback()
            print('rollback')
            str_fields = ''
            for field in fields:
                str_fields += str(field)
            logging.info(
                'insert_row into ' + table + ' rollback- params: ' +
                str_fields
            )
        else:
            print('commit')
            self.session.commit()
        return new_row

    def get_line_items(self, from_date, to_date, org_list = [], invoiced = False):
        line_item = util.get_table('line_item')
        price_item = util.get_table('price_item')
        service_type = util.get_table('service_type')
        order = util.get_table('order')
        order_charge_method = util.get_table('order_charge_method')
        charge_method = util.get_table('charge_method')
        charge_method_type = util.get_table('charge_method_type')
        invoice = util.get_table('invoice')
        institution = util.get_table('institution')
        filters = [
            line_item.active == 1,
            line_item.date_created >= from_date,
            line_item.date_created < to_date,
            line_item.price_per_unit > 0,
            order.active == 1,
            order.billable == 1
        ]
        if invoiced:
            filters.append(invoice.id != None)
        if org_list:
            filters.append(models.Organization.name.in_(org_list))
        res = (self.session.query(line_item, price_item, service_type, order,
            order_charge_method, charge_method, charge_method_type, models.User,
            models.Organization, models.OrganizationType, invoice, institution,
            models.Department)
                # limit natural joins so that we get errors rather than omit
                # billing something that has missing data
                .join((order, line_item.order_id == order.id)
                )
                .outerjoin( (models.Organization, line_item.organization_id ==
                        models.Organization.id),
                    (models.OrganizationType, models.Organization.organization_type_id ==
                        models.OrganizationType.id),
                    (invoice, invoice.id == line_item.invoice_id),
                    (price_item, line_item.price_item_id == price_item.id),
                    (service_type, price_item.service_type_id ==
                        service_type.id),
                    (order_charge_method, order.id == order_charge_method.order_id),
                    (charge_method, order_charge_method.charge_method_id == charge_method.id),
                    (charge_method_type, charge_method.charge_method_type_id == charge_method_type.id),
                    (models.User, models.User.id == order.submitter_id),
                    (institution, institution.id == models.Organization.institution_id),
                    (models.Department, models.Department.id ==
                        models.Organization.department_id)
                )
            .filter(*filters).order_by((line_item.invoice_id == None), line_item.invoice_id, models.Organization.name, charge_method.id).all())
        return res

    def get_charge_method(self, order_id):
        order_charge_method = util.get_table('order_charge_method')
        order = util.get_table('order')
        charge_method = util.get_table('charge_method')
        charge_method_type = util.get_table('charge_method_type')
        res = (self.session.query(order, order_charge_method, charge_method,
            charge_method_type)
                .join(order_charge_method, charge_method, charge_method_type)
            .filter(order_charge_method.order_id == order_id, charge_method.active == 1)
            .order_by(order.date_created, order_charge_method.percent.desc()).all())
        return res

    def get_org_position(self, org_id, position_name):
        res = (self.session.query(models.User)
                .join(models.UserOrganization,
                    models.UserOrganizationPosition,
                    models.Position)
            .filter((models.UserOrganization.user_organization_id == org_id),
                (models.Position.name == position_name)).all())
        return res

    def get_org_billing_address(self, org_id):
        res = (self.session.query(models.Address)
                .join(models.Organization, models.Organization.billing_address_id ==
                    models.Address.id)
            .filter((models.Organization.id == org_id)).first())
        return res

