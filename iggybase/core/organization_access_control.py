from flask import g, current_app
from sqlalchemy import DateTime, func
from iggybase.database import db_session
from iggybase.admin import models
from iggybase import utilities as util
from sqlalchemy.orm import aliased
from collections import OrderedDict
import json
import logging
import time

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__(self):
        self.org_ids = []
        self.current_org_id = None
        self.session = db_session()

        if g.user is not None and not g.user.is_anonymous:
            self.user =  self.session.query(models.User).filter_by(id=g.user.id).first()

            # must distinguish user level orgs from group level org ids
            query = self.session.query(models.Organization.parent_id.distinct().label('parent_id'))
            self.parent_orgs = [row.parent_id for row in query.all()]
            facility_root_org_id = g.root_org_id

            user_orgs = self.session.query(models.UserOrganization).filter_by(active=1, user_id=self.user.id).all()

            facility_orgs = {}
            for user_org in user_orgs:
                if user_org.user_organization_id is not None:
                    level = self.get_facility_orgs(user_org.user_organization_id, facility_root_org_id, 0)
                    if level is not None:
                        facility_orgs[user_org.user_organization_id] = level

            self.current_org_id = None
            min_level = None
            for user_org, level in facility_orgs.items():
                # levels are ordered from high to low, hightest has order = 1
                if min_level is None or (level < min_level and user_org != self.user.organization_id):
                    # TODO: do we really want min level.id or do we want the lowest
                    # level.order
                    min_level = level
                    self.current_org_id = user_org
                self.get_child_organization(user_org)
            g.current_org_id = self.current_org_id
        else:
            self.user = None

    def __del__ (self):
        self.session.commit()

    def commit(self):
        self.session.commit()

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

    def get_instance_data(self, table_object, criteria):
        for field, value in criteria.items():
            if field == 'name' and value == 'new':
                return table_object()
            else:
                res = self.session.query(table_object). \
                        filter(getattr(table_object, field) == value). \
                        filter(getattr(table_object, 'organization_id').in_(self.org_ids)).first()

                if res:
                    return res
                else:
                    return table_object()

    def get_select_list(self, select_list_id, active=1):
        select_list_items = self.session.query(models.SelectListItem).\
            filter_by(select_list_id=select_list_id). \
            filter_by(active=active).all()

        results = [(-99, '')]

        for row in select_list_items:
            results.append((row.id, row.display_name))

        return results

    def get_foreign_key_data(self, fk_table_id, fk_field_display, params=None):
        fk_table_data = self.session.query(models.TableObject).filter_by(id=fk_table_id).first()
        fk_field_data = self.foreign_key(fk_table_id, fk_field_display)

        results = [(-99, '')]
        if fk_field_data is not None:
            fk_table_object = util.get_table(fk_table_data.name)

            if params is None:
                rows = self.session.query(getattr(fk_table_object, 'id'),
                                                         getattr(fk_table_object, fk_field_data['foreign_key']).
                                          label('name')).all()
            else:
                criteria = []
                for key, value in params.items():
                    criteria.append(getattr(fk_table_object, key) == value)

                rows = self.session.query(getattr(fk_table_object, 'id'),
                                          getattr(fk_table_object,
                                                  fk_field_data['foreign_key'])).filter(*criteria).all()

            for row in rows:
                results.append((row.id, row.name))

        return results

    def get_table_query_data(self, field_dict, criteria={}):
        results = []
        tables = set([])
        table_models = {}
        joins = set([])
        outer_joins = []
        columns = []
        fk_columns = []
        aliases = {}
        wheres = []
        first_table_named = None  # set to first table name, dont add to joins
        for field in field_dict.values():
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
                alias_name = field.Field.display_name + '_' + field.FK_TableObject.name + '_' + field.FK_Field.display_name
                aliases[alias_name] = aliased(table_model)
                outer_joins.append((
                    aliases[alias_name],
                    getattr(fk_table_model, field.Field.display_name) == aliases[alias_name].id
                ))
                col = getattr(aliases[alias_name],
                    field.FK_Field.display_name)
                columns.append(col.label(field.name))
                criteria_key = (field.FK_TableObject.name, field.FK_Field.display_name)

            else:  # non-fk field
                tables.add(table_model)
                col = getattr(table_model, field.Field.display_name)
                if field.type == 'file': # give name as well
                    col = getattr(table_model, 'name') + '/' + col

                columns.append(col.label(field.name))
                                # add to joins if not first table, avoid joining to self
                if (not first_table_named
                    or (first_table_named == field.TableObject.name)):
                    first_table_named = field.TableObject.name
                else:
                    joins.add(table_model)
                criteria_key = (field.TableObject.name, field.Field.display_name)

            # don't include criteria for self foreign keys
            if criteria_key in criteria and not (field.is_foreign_key and
                    field.TableObject.name == first_table_named):
                if type(criteria[criteria_key]) is list:
                    wheres.append(col.in_(criteria[criteria_key]))
                if type(criteria[criteria_key]) is dict:
                    if ('from' in criteria[criteria_key]
                        and 'to' in criteria[criteria_key]
                    ):
                        wheres.extend([col >= criteria[criteria_key]['from'],
                            col <= criteria[criteria_key]['to']])
                    if( 'compare' in criteria[criteria_key]
                        and 'value' in criteria[criteria_key]
                    ):
                        if criteria[criteria_key]['compare'] == 'greater than':
                            wheres.append(col > criteria[criteria_key]['value'])
                else:
                    wheres.append(col == criteria[criteria_key])
        # add organization id checks on all tables, does not include fk tables
        for table_model in tables:
            # add a row id that is the id of the first table named
            if (table_model.__table__.name.lower() == first_table_named):
                col = getattr(table_model, 'id')
                columns.append(col.label('DT_RowId'))
            wheres.append(getattr(table_model, 'organization_id').in_(self.org_ids))
        start = time.time()
        results = (
            self.session.query(*columns).
                join(*joins).
                outerjoin(*outer_joins).
                filter(*wheres).all()
        )
        print('query: ' + str(time.time() - start))
        return results

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

        return table.query.filter(*filters).order_by(getattr(table, 'name'))

    def get_long_text(self, lt_id):
        table = util.get_table("long_text")

        return table.query.filter_by(id=lt_id).first()

    def get_new_name(self, table_name):
        table_object = util.get_table('table_object')

        table_instance = self.session.query(table_object).filter_by(name = table_name).first()
        instance_name = table_instance.get_new_name()

        self.session.add(table_instance)
        self.session.flush()

        return instance_name

    def save_data_instance(self, instance):
        self.session.add(instance)
        self.session.flush()

        save_msg = {'id': instance.id, 'name': instance.name, 'table': instance.__tablename__}

        return save_msg

    def get_row_id(self, table_name, params):
        result = self.get_row(table_name, params)
        if result:
            return result.id
        else:
            return None

    def get_row(self, table_name, params):
        table_object = util.get_table(table_name)

        criteria = []

        for key, value in params.items():
            criteria.append(getattr(table_object, key) == value)

        result = self.session.query(table_object).filter(*criteria).first()

        return result

    def get_table_by_id(self, table_id):
        table_object = util.get_table('table_object')

        criteria = [getattr(table_object, 'id') == table_id]

        result = self.session.query(table_object).filter(*criteria).first()

        return result

    def get_child_row_names(self, child_table_name, child_link_field_id, parent_ids):
        field = self.session.query(models.Field).filter_by(id=child_link_field_id).first()

        child_table = util.get_table(child_table_name)
        parent_column = getattr(child_table, field.display_name)

        # logging.info('child_table_name: ' + child_table_name)
        # logging.info('parent_column.name: ' + parent_column.name)

        rows = self.session.query(child_table).filter(parent_column.in_(parent_ids)).order_by('order', 'name').all( )

        names = OrderedDict()
        for row in rows:
            names[row.id] = row.name

        return names

    def update_obj_rows(self, items, updates):
        updated = []
        for item in items:
            row_updates = []
            for col, val in updates.items():
                try:
                    setattr(item, col, val)
                    row_updates.append(col)
                except AttributeError:
                    print('failed to update')
            # commit if we were able to make all updates for the row
            if len(updates) == len(row_updates):
                self.session.commit()
                updated.append(item.id)
                # change table version in cache
                current_app.cache.increment_version([item.__tablename__])
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
        parent_id = None
        try:
            for item in save_items:
                table_object_id = self.session.query(models.TableObject.id).filter_by(name=item['table']).first()[0]
                old_item_exists = None
                if work_items:
                    # see if item already saved
                    for old_item in work_items:
                        if old_item.WorkItem.table_object_id == table_object_id and old_item.WorkItem.row_id == item['id']:
                            old_item_exists = old_item
                            break
                            continue # don't need to add this one it is already there

                    # see if a null row exists, and update row_id
                    for i, old_item in enumerate(work_items):
                        if old_item.WorkItem.table_object_id == table_object_id and old_item.WorkItem.row_id == None:
                            old_item_exists = old_item
                            work_items.pop(i)
                            break

                if old_item_exists:
                    old_item_row = self.session.query(models.WorkItem).filter_by(id=old_item_exists.WorkItem.id).first()
                    setattr(old_item_row, 'row_id', item['id'])
                else: # insert new row
                    new_name = work_item_table_object.get_new_name()
                    if parent:
                        parent_table_object_id = self.session.query(models.TableObject.id).filter_by(name=parent['table']).first()[0]
                        filters = [
                                (models.WorkItem.work_item_group_id == work_item_group_id),
                                (models.WorkItem.table_object_id ==
                                    parent_table_object_id),
                                (models.WorkItem.row_id == parent['id'])

                        ]
                        parent_id = self.session.query(models.WorkItem.id).filter(*filters).first()[0]
                    new_row = table_model(name = new_name, active = 1,
                            organization_id = self.current_org_id, work_item_group_id = work_item_group_id,
                            table_object_id = table_object_id, row_id = item['id'],
                            parent_id = parent_id)
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

    def get_step_actions(self, step_id, timing):
        return (self.session.query(models.StepAction)
                .filter(
                    models.StepAction.step_id==step_id,
                    models.StepAction.timing == timing
                ).order_by(models.StepAction.order).all())

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
        # ensure one inserts under ones current_org_id
        fields['organization_id'] = self.current_org_id
        try:
            new_name = table_table_object.get_new_name()
            new_row = table_model(name = new_name, **fields)
            self.session.add(new_row)
        except:
            self.session.rollback()
            print('rollback')
            logging.info(
                'insert_row into ' + table + ' rollback- params: ' +
                json.dumps(fields)
            )
        else:
            print('commit')
            self.session.commit()
        return new_row

    def get_line_items(self, from_date, to_date, org_list = []):
        line_item = util.get_table('line_item')
        price_item = util.get_table('price_item')
        order = util.get_table('order')
        order_charge_method = util.get_table('order_charge_method')
        charge_method = util.get_table('charge_method')
        charge_method_type = util.get_table('charge_method_type')
        invoice = util.get_table('invoice')
        filters = [
            line_item.active == 1,
            line_item.date_created >= from_date,
            line_item.date_created <= to_date
        ]
        if org_list:
            filters.append(models.Organization.name.in_(org_list))

        res = (self.session.query(line_item, price_item, order,
            order_charge_method, charge_method, charge_method_type, models.User,
            models.Organization, models.OrganizationType, invoice)
                .join((price_item, line_item.price_item_id == price_item.id),
                    (order, line_item.order_id == order.id),
                    (order_charge_method, order.id == order_charge_method.order_id),
                    (charge_method, order_charge_method.charge_method_id == charge_method.id),
                    (charge_method_type, charge_method.charge_method_type_id == charge_method_type.id),
                    (models.User, models.User.id == order.submitter_id),
                    (models.Organization, line_item.organization_id ==
                        models.Organization.id),
                    (models.OrganizationType, models.Organization.organization_type_id ==
                        models.OrganizationType.id)
                )
                .outerjoin(invoice, invoice.id == line_item.invoice_id)
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


