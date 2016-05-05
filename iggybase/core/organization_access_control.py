from flask import g, request, current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import DateTime, func
from iggybase.database import db_session
from iggybase.admin import models
from iggybase import models as core_models
from iggybase import utilities as util
from sqlalchemy.orm import aliased
import re
import datetime
import sys
import logging
import time
import random


# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__(self):
        self.org_ids = []
        self.current_org_id = None
        self.session = db_session()

        if g.user is not None and not g.user.is_anonymous:
            role_access_control = util.get_role_access_control()

            self.user =  self.session.query(models.User).filter_by(id=g.user.id).first()
            query = self.session.query(models.Organization.parent_id.distinct().label('parent_id'))
            self.parent_orgs = [row.parent_id for row in query.all()]

            facility_root_org_id = role_access_control.facility.root_organization_id

            user_orgs = self.session.query(models.UserOrganization).filter_by(active=1, user_id=self.user.id).all()

            facility_orgs = {}
            for user_org in user_orgs:
                if user_org.user_organization_id is not None:
                    level = self.get_facility_orgs(user_org.user_organization_id, facility_root_org_id, 0)
                    if level is not None:
                        facility_orgs[user_org.user_organization_id] = level

            self.current_org_id = user_org
            min_level = None
            for user_org, level in facility_orgs.items():
                # logging.info('facility_orgs: ' + str(user_org))
                if min_level is None or (level < min_level and user_org != self.user.organization_id):
                    min_level = level
                    self.current_org_id = user_org
                self.get_child_organization(user_org)

            # logging.info('self.current_org_id: ' + str(self.current_org_id))
        else:
            self.user = None

    def __del__ (self):
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

    def get_entry_data(self, table_name, params):
        field_data = self.get_field_data(table_name)
        results = None
        if field_data is not None:
            table_object = util.get_table(table_name)

            columns = []
            for row in field_data:
                field_display_name = util.get_field_attr(row.Field,
                    row.FieldRole, 'display_name')
                columns.append(getattr(table_object, row.Field.display_name).\
                               label(field_display_name))

            if len(columns) == 0:
                return results

            criteria = [getattr(table_object, 'organization_id').in_(self.org_ids)]

            for key, value in params.items():
                criteria.append(getattr(table_object, key) == value)

            results = self.session.query(*columns).filter(*criteria).all()
        return results

    def get_select_list(self, select_list_id, active=1):
        select_list_items = self.session.query(models.SelectListItem).\
            filter_by(select_list_id=select_list_id). \
            filter_by(active=active).all()

        results = [(-99, '')]

        for row in select_list_items:
            results.append((row.id, row.display_name))

        return results

    def get_foreign_key_data(self, fk_table_id, params=None):
        fk_table_data = self.session.query(models.TableObject).filter_by(id=fk_table_id).first()
        fk_field_data = self.foreign_key(fk_table_id)

        results = [(-99, '')]
        if fk_field_data is not None:
            fk_table_object = util.get_table(fk_table_data.name)

            if params is None:
                rows = self.session.query(getattr(fk_table_object, 'id'),
                                                         getattr(fk_table_object, 'name')).all()
            else:
                criteria = []
                for key, value in params.items():
                    criteria.append(getattr(fk_table_object, key) == value)

                rows = self.session.query(getattr(fk_table_object, 'id'), getattr(fk_table_object, 'name')). \
                    filter(*criteria).all()

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
            if field.TableObject.name in table_models:
                table_model = table_models[field.TableObject.name]
            else:
                table_model = util.get_table(field.TableObject.name)
                table_models[field.TableObject.name] = table_model
            if field.is_foreign_key:
                if field.fk_table.name in table_models:
                    fk_table_model = table_models[field.fk_table.name]
                else:
                    fk_table_model = util.get_table(field.fk_table.name)
                    table_models[field.fk_table.name] = fk_table_model
                # create alias to the fk table
                # solves the case of more than one join to same table
                alias_name = field.fk_field.display_name + '_' + field.TableObject.name + '_' + field.Field.display_name
                aliases[alias_name] = aliased(table_model)
                outer_joins.append((
                    aliases[alias_name],
                    getattr(fk_table_model, field.fk_field.display_name) == aliases[alias_name].id
                ))
                col = getattr(aliases[alias_name],
                    field.Field.display_name)
                # TODO: validate that tablequeries don't allow dup display names
                columns.append(col.label(field.display_name))

            else:  # non-fk field
                tables.add(table_model)
                col = getattr(table_model, field.Field.display_name)
                columns.append(col.label(field.display_name))
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
            #if criteria_key in criteria:
                if type(criteria[criteria_key]) is list:
                    wheres.append(col.in_(criteria[criteria_key]))
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

    def get_field_data(self, table_name):
        role_access_control = util.get_role_access_control()
        table_data = role_access_control.has_access('TableObject', {'name': table_name})
        field_data = None

        if table_data is not None:
            field_data = role_access_control.fields(table_data.id)

        return field_data

    def get_search_field_data(self, table_name, search_display_name):
        role_access_control = util.get_role_access_control()
        table_data = role_access_control.has_access('TableObject', {'name': table_name})

        if table_data is not None:
            field_data = role_access_control.fields(table_data.id,
                                                    {'field.display_name': search_display_name})

            if field_data is not None:
                search_table = role_access_control.has_access('TableObject',
                                                              {'id': field_data[0].Field.foreign_key_table_object_id})

                if search_table is not None:
                    search_table_data = self.foreign_key(search_table.id)
                    search_field_data = role_access_control.fields(search_table.id,
                                                                   {'field_role.search_field': 1})

                    return search_table_data['name'], search_field_data

        return None, None, None

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

    def save_form(self):
        role_access_control = util.get_role_access_control()

        long_text_data = models.TableObject.query.filter_by(name='long_text').first()

        history_data = models.TableObject.query.filter_by(name='history').first()

        # fields contain the data that was displayed on the form and possibly edited
        fields = {}
        # fields contain the data that was displayed on the form and possibly edited
        table_field_data = {}
        # keeps track of the tables that store the data
        table_defs = {}
        # keeps track of the table object data for tables that store the child data used for generating the auto IDs
        table_objects = {}
        # all the data to be saved as an instance of the sqlalchemy table
        instances = {}
        # tracks whether a row was modified
        row_modified = {}

        # used to identify fields that contain data that needs to be saved
        field_pattern = re.compile('(data_entry|record_data|old_value)_(\S+)_(\d+)')
        for key in request.form:
            data = request.form.get(key)

            # logging.info(key + ': ' + data)

            if key.startswith('bool_'):
                key = key[key.index('_') + 1:]

            field_id = field_pattern.match(key)
            if field_id is not None:
                # logging.info('key: ' + key)
                if field_id.group(3) not in fields.keys():
                    fields[field_id.group(3)] = {'data_entry': {}, 'record_data': {}, 'old_value': {}}

                fields[field_id.group(3)][field_id.group(1)][field_id.group(2)] = data

        # for key1, value1 in fields.items():
        #     for key2, value2 in value1.items():
        #         for key3, value3 in value2.items():
        #             logging.info(str(key1) + ' ' + str(key2) + ' ' + str(key3) + ': ' + str(value3))

        try:
            for row_id in sorted(fields.keys()):
                row_data = fields[row_id]

                table_name_field = row_data['record_data']['table_name']
                table_id_field = row_data['record_data']['table_id']
                current_inst_name = row_data['record_data']['row_name']

                if table_id_field not in table_defs.keys():
                    table_field_data[table_id_field] = {}
                    temp_field_data = role_access_control.fields(table_id_field)
                    for field in temp_field_data:
                        table_field_data[table_id_field][field.Field.display_name] = field.Field

                    table_objects[table_id_field] = util.get_table(table_name_field)
                    table_defs[table_id_field] = self.session.query(models.TableObject).\
                        filter_by(name=table_objects[table_id_field].__tablename__).first()

                current_table_object = table_objects[table_id_field]
                current_table_data = table_defs[table_id_field]
                current_field_data = table_field_data[table_id_field]

                if row_id not in instances:
                    if current_inst_name == 'new' or current_inst_name == '':
                        instances[row_id] = current_table_object()
                        setattr(instances[row_id], 'date_created', datetime.datetime.utcnow())

                        if 'name' in row_data['data_entry'].keys() and row_data['data_entry']['name'] != '' and \
                                        row_data['data_entry']['name'] != 'new':
                            current_inst_name = row_data['data_entry']['name']
                        elif current_table_data.new_name_prefix is not None and \
                                        current_table_data.new_name_prefix != "":
                            current_inst_name = current_table_data.get_new_name()
                            self.session.add(current_table_data)
                            self.session.flush()
                        else:
                            current_inst_name = table_name_field + str(random.randint(1000000000, 9999999999))

                        row_data['data_entry']['name'] = current_inst_name
                    else:
                        instances[row_id] = self.session.query(current_table_object). \
                            filter_by(name=current_inst_name).first()

                        if row_data['old_value']['date_created'] == '':
                            setattr(instances[row_id], 'date_created', datetime.datetime.utcnow())

                    setattr(instances[row_id], 'last_modified', datetime.datetime.utcnow())

                # logging.info('current_inst_name: ' + current_inst_name)
                # logging.info('row_data[data_entry][name]: ' + row_data['data_entry']['name'])

                if 'organization_id' in row_data['data_entry'].keys():
                    row_org_id = row_data['data_entry']['organization_id']
                elif 'organization_id' in row_data['old_value'].keys():
                    row_org_id = row_data['old_value']['organization_id']
                elif self.current_org_id is not None:
                    row_org_id = self.current_org_id
                else:
                    row_org_id = 1

                if not isinstance(row_org_id, int):
                    if current_field_data['organization_id'].foreign_key_display is None:
                        org_display = 'name'
                    else:
                        org_display = field_data[table_id_field]['organization_id'].Field.foreign_key_display

                    org_data = (self.session.query(models.Organization).
                                filter(getattr(models.Organization, org_display) == row_org_id).first())

                    if org_data is None:
                        row_org_id = 1
                    else:
                        row_org_id = org_data.id

                row_data['data_entry']['organization_id'] = row_org_id

                row_modified[row_id] = False

                for field, field_data in current_field_data.items():
                    # only update fields that were on the form
                    if field not in row_data['data_entry'].keys():
                        if field in row_data['old_value'].keys():
                            row_data['data_entry'][field] = row_data['old_value'][field]
                        else:
                            continue

                    if field_data.foreign_key_table_object_id == long_text_data.id and \
                                    row_data['data_entry'][field] != '':
                        if row_data['old_value'][field] == '':
                            lt = core_models.LongText()
                            setattr(lt, 'name', long_text_data.get_new_name())
                            setattr(lt, 'date_created', datetime.datetime.utcnow())
                        else:
                            lt_id = row_data['old_value'][field]
                            lt = self.session.query(core_models.LongText).filter_by(id=lt_id).first()

                        setattr(lt, 'organization_id', row_org_id)
                        setattr(lt, 'last_modified', datetime.datetime.utcnow())
                        setattr(lt, 'long_text', row_data['data_entry'][field])
                        self.session.add(lt)
                        self.session.flush()
                        lt_id = lt.id
                        setattr(instances[row_id], field, lt_id)
                    elif field_data.foreign_key_table_object_id is not None:
                        try:
                            # TODO find a better way to deal with no value in a select
                            # a top row is is added to all selects with an index of -99 (get_foreign_key_data)
                            if int(row_data['data_entry'][field]) == -99:
                                setattr(instances[row_id], field, None)
                                row_data['data_entry'][field] = None
                            else:
                                setattr(instances[row_id], field, int(row_data['data_entry'][field]))
                        except ValueError:
                            if field_data.foreign_key_display is None:
                                fk_display = 'name'
                            else:
                                fk_display = field_data.foreign_key_display

                            fk_id = []
                            if row_data['data_entry'][field] is not None and row_data['data_entry'][field] != '':
                                fk_id = self.get_foreign_key_data(field_data.foreign_key_table_object_id,
                                                                  {fk_display: row_data['data_entry'][field]})

                            if len(fk_id) == 0 or len(fk_id[0]) == 0:
                                setattr(instances[row_id], field, None)
                                row_data['data_entry'][field] = None
                            else:
                                setattr(instances[row_id], field, fk_id[1][0])
                                row_data['data_entry'][field] = fk_id[1][0]
                    elif field != 'id' and field != 'last_modified' and field != 'date_created':
                        if row_data['data_entry'][field] is None or row_data['data_entry'][field] == '':
                            setattr(instances[row_id], field, None)
                        elif field_data.data_type_id == 1:
                            setattr(instances[row_id], field, int(row_data['data_entry'][field]))
                        elif field_data.data_type_id == 8:
                            setattr(instances[row_id], field, float(row_data['data_entry'][field]))
                        elif field_data.data_type_id == 3:
                            if row_data['data_entry'][field] == 'y':
                                setattr(instances[row_id], field, 1)
                                row_data['data_entry'][field] = True
                            else:
                                setattr(instances[row_id], field, None)
                                row_data['data_entry'][field] = None
                        else:
                            setattr(instances[row_id], field, row_data['data_entry'][field])

                    if field != 'last_modified' and field != 'date_created' and \
                            not (row_data['old_value'][field] == row_data['data_entry'][field] or
                                 row_data['old_value'][field] == str(row_data['data_entry'][field]) or
                                 (row_data['record_data']['row_name'] == 'new' and
                                  row_data['data_entry'][field] is None)):

                        if not(row_data['record_data']['row_name'] == 'new' and field in ['name', 'organization_id']):
                            row_modified[row_id] = True

                        # logging.info('field: ' + field + '  old vlaue: ' + str(row_data['old_value'][field]) +
                        #              '  new value: ' + str(row_data['data_entry'][field]))

                        history_instance = core_models.History()
                        history_instance.name = history_data.get_new_name()
                        history_instance.date_created = datetime.datetime.utcnow()
                        history_instance.last_modified = datetime.datetime.utcnow()
                        history_instance.table_object_id = table_id_field
                        history_instance.field_id = field_data.id
                        history_instance.organization_id = row_org_id
                        history_instance.user_id = g.user.id
                        history_instance.instance_name = current_inst_name
                        history_instance.old_value = row_data['old_value'][field]
                        history_instance.new_value = row_data['data_entry'][field]
                        self.session.add(history_instance)
                        self.session.flush

            self.session.add(history_data)
            self.session.flush()

            row_names = {}
            table_names = set()
            for row_id in sorted(instances.keys()):
                instance = instances[row_id]
                if row_modified[row_id]:
                    self.session.add(instance)
                    self.session.flush()

                    row_names[row_id] = {'name': instance.name, 'table': instance.__tablename__}
                    table_names.add(instance.__tablename__)
                elif instance.name is not None:
                    row_names[row_id] = {'name': instance.name, 'table': instance.__tablename__}
                    table_names.add(instance.__tablename__)

            self.session.commit()
            # change table version in cache
            current_app.cache.increment_version(list(table_names))
            return row_names
        except:
            self.session.rollback()
            err = sys.exc_info()[0]
            raise
            logging.error(err)
            return [['error',err]]

    def get_row_id(self, table_name, params):
        table_object = util.get_table(table_name)

        criteria = []

        for key, value in params.items():
            criteria.append(getattr(table_object, key) == value)

        result = self.session.query(table_object).filter(*criteria).first()

        if result:
            return result.id
        else:
            return None

    def get_child_row_names(self, child_table_name, child_link_field_id, parent_id):
        field = self.session.query(models.Field).filter_by(id=child_link_field_id).first()

        child_table = util.get_table(child_table_name)

        rows = self.session.query(child_table).filter(getattr(child_table, field.display_name) == parent_id).all( )

        names = []
        for row in rows:
            names.append(row.name)

        return names

    def update_table_rows(self, updates, ids, table):
        ids.sort()
        table_model = util.get_table(table)
        rows = table_model.query.filter(table_model.id.in_(ids), getattr(table_model, 'organization_id').in_(self.org_ids)).order_by('id').all()

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
                    pass
            # commit if we were able to make all updates for the row
            if len(updates) == len(row_updates):
                self.session.commit()
                updated.append(ids[i])
                # change table version in cache
                current_app.cache.increment_version([table])
            else:
                self.session.rollback()
        return updated

    def update_step(self, group_id, step, workflow_id):
        table_model = util.get_table('work_item_group')
        res = (self.session.query(models.Workflow, models.Step).
               join(models.Step).
               filter(models.Step.order == step, models.Workflow.id ==
                   workflow_id).first())
        step_id = res.Step.id
        work_item_group = table_model.query.filter(table_model.id == group_id, getattr(table_model, 'organization_id').in_(self.org_ids)).first()
        updated = False
        try:
            setattr(work_item_group, 'step_id', res.Step.id)
            updated = True
        except AttributeError:
            pass
        if updated:
            self.session.commit()
        return updated

    def save_work_items(self, work_item_group_id, save_items, parent):
        table_model = util.get_table('work_item')
        work_item_table_object = self.session.query(models.TableObject).filter_by(name='work_item').first()
        table_object_id = None
        success = False
        try:
            for item in save_items:
                table_object_id = self.session.query(models.TableObject.id).filter_by(name=item['table']).first()[0]
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
                new_row = table_model(name= new_name, active=1,
                        organization_id=1, work_item_group_id = work_item_group_id,
                        table_object_id = table_object_id, row_id = item['id'],
                        parent_id = parent_id)
                self.session.add(new_row)
        except:
            print('rollback')
            self.session.rollback()
        else:
            print('commit')
            self.session.commit()
            success = True
        return success

    def get_step_actions(self, step_id):
        return self.session.query(models.StepAction).filter_by(step_id=step_id).all()

    def get_attr_from_id(self, table_object_id, row_id, attr):
        table_object = self.session.query(models.TableObject).filter_by(id=table_object_id).first()
        table_model = util.get_table(table_object.name)
        row = self.session.query(table_model).filter_by(id=row_id).first()
        return getattr(row, attr)

