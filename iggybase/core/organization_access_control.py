from flask import g, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import DateTime, func
from iggybase.core.role_access_control import RoleAccessControl
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


# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__(self):
        self.org_ids = []
        self.current_org_id = None
        self.session = db_session()
        if g.user is not None and not g.user.is_anonymous:
            self.user =  self.session.query(models.User).filter_by(id=g.user.id).first()
            query = self.session.query(models.Organization.parent_id.distinct().label('parent_id'))
            self.parent_orgs = [row.parent_id for row in query.all()]

            user_orgs = self.session.query(models.UserOrganization).filter_by(active=1, user_id=self.user.id).all()

            for user_org in user_orgs:
                if user_org.user_organization_id is not None:
                    self.get_child_organization(user_org.user_organization_id)
                    if user_org.default_organization == 1:
                        self.current_org_id = user_org.user_organization_id
        else:
            self.user = None

    def __del__ (self):
        self.session.commit()

    def get_child_organization(self, parent_organization_id):
        self.org_ids.append(parent_organization_id)
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
                columns.append(getattr(table_object, row.Field.field_name).\
                               label(row.FieldRole.display_name))

            criteria = [getattr(table_object, 'organization_id').in_(self.org_ids)]

            for key, value in params.items():
                criteria.append(getattr(table_object, key) == value)

            results = self.session.query(*columns).filter(*criteria).all()

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
                alias_name = field.fk_field.field_name + '_' + field.TableObject.name + '_' + field.Field.field_name
                aliases[alias_name] = aliased(table_model)
                outer_joins.append((
                    aliases[alias_name],
                    getattr(fk_table_model, field.fk_field.field_name) == aliases[alias_name].id
                ))
                col = getattr(aliases[alias_name],
                    field.Field.field_name)
                # TODO: validate that tablequeries don't allow dup display names
                columns.append(col.label(field.display_name))

            else:  # non-fk field
                tables.add(table_model)
                col = getattr(table_model, field.Field.field_name)
                columns.append(col.label(field.display_name))
                                # add to joins if not first table, avoid joining to self
                if (not first_table_named
                    or (first_table_named == field.TableObject.name)):
                    first_table_named = field.TableObject.name
                else:
                    joins.add(table_model)

            criteria_key = (field.TableObject.name, field.Field.field_name)
            if criteria_key in criteria:
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
            filters.append(models.Field.field_name == 'name')
        else:
            filters.append(models.Field.id == display)
        res = (self.session.query(models.Field, models.TableObject).
               join(models.TableObject, models.TableObject.id == models.Field.table_object_id).
               join(models.TableObjectRole, models.TableObject.id == models.TableObjectRole.table_object_id).
               filter(*filters).first())
        return {'foreign_key': res.Field.field_name,
                'name': res.TableObject.name
                }

    def get_field_data(self, table_name):
        role_access_control = RoleAccessControl()
        table_data = role_access_control.has_access('TableObject', {'name': table_name})
        field_data = None

        if table_data is not None:
            field_data = role_access_control.fields(table_data.id)

        return field_data

    def get_search_field_data(self, table_name, search_field_name):
        role_access_control = RoleAccessControl()
        table_data = role_access_control.has_access('TableObject', {'name': table_name})

        if table_data is not None:
            field_data = role_access_control.fields(table_data.id,
                                                    {'field.field_name': search_field_name})

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
        role_access_control = RoleAccessControl()

        long_text_data = models.TableObject.query.filter_by(name='long_text').first()

        history_data = models.TableObject.query.filter_by(name='history').first()

        # fields contain the data that was displayed on the form and possibly edited
        fields = {}
        # fields contain the data that was displayed on the form and possibly edited
        field_data = {}
        # record fields contain the record data (table name, id and record name)
        record_fields = {}
        # hidden fields contain the old values
        old_fields = {}
        # keeps track of the tables that store the data
        table_defs = {}
        # keeps track of the row organization ids
        row_org_id = {}
        # keeps track of the table object data for tables that store the child data used for generating the auto IDs
        table_objects = {}
        # all the data to be saved as an instance of the sqlalchemy table
        instances = {}

        # used to identify fields that contain data that needs to be saved
        field_pattern = re.compile('(\S+)_(\d+)')
        for key in request.form:
            data = request.form.get(key)
            if key.startswith('bool_'):
                key = key[key.index('_') + 1:]

            if key.startswith('record_data_'):
                # trim record_data_
                field_id = key[12:]
                record_fields[field_id]=data
            elif key.startswith('old_value_'):
                # trim old_value_
                field_id = key[10:]
                old_fields[field_id] = data
            elif key.startswith('data_entry_'):
                # trim data_entry_
                field_id = key[11:]
                fields[field_id] = data

        try:
            for field, data in fields.items():
                row_id = int(field[field.rindex('_') + 1:])
                column_name = field[:field.rindex('_')]

                table_name_field = record_fields['table_name_' + str(row_id)]
                table_id_field = record_fields['table_id_' + str(row_id)]
                current_inst_name = record_fields['row_name_' + str(row_id)]

                if table_id_field not in table_defs.keys():
                    field_data[table_id_field] = {}
                    field_data[table_id_field]['organization_id'] = role_access_control.\
                        fields(table_id_field, {'field.field_name': 'organization_id'})[0]
                    table_objects[table_id_field] = util.get_table(table_name_field)
                    table_defs[table_id_field] = self.session.query(models.TableObject).\
                        filter_by(name=table_objects[table_id_field].__tablename__).first()

                current_table_object = table_objects[table_id_field]
                current_table_data = table_defs[table_id_field]

                if column_name not in field_data[table_id_field].keys():
                    field_data[table_id_field][column_name] = role_access_control.\
                        fields(table_id_field, {'field.field_name': column_name})[0]

                if row_id not in row_org_id.keys():
                    try:
                        float(fields['organization_id_' + str(row_id)])
                        row_org_id[row_id] = fields['organization_id_' + str(row_id)]
                    except ValueError:
                        if fields['organization_id_' + str(row_id)] != '' and\
                                        fields['organization_id_' + str(row_id)] is not None:
                            if field_data[table_id_field]['organization_id'].Field.foreign_key_display is None:
                                org_display = 'name'
                            else:
                                org_display = field_data[table_id_field]['organization_id'].Field.foreign_key_display

                            org_data = self.session.query(models.Organization).filter(getattr(models.Organization,
                                                                                              org_display)==
                                                                                      fields['organization_id_' +
                                                                                             str(row_id)]).first()

                            row_org_id[row_id] = org_data.id
                        elif self.current_org_id is not None:
                            row_org_id[row_id] = self.current_org_id
                        else:
                            row_org_id[row_id] = 1

                if row_id not in instances:
                    if current_inst_name == 'new':
                        name_field = fields['name_' + str(row_id)]

                        instances[row_id] = current_table_object()

                        setattr(instances[row_id], 'date_created', datetime.datetime.utcnow())
                        if current_table_data.new_name_prefix is not None and current_table_data.new_name_prefix != "":
                            if fields['name_' + str(row_id)] == 'new' or \
                                            fields['name_' + str(row_id)] == '':
                                current_inst_name = current_table_data.get_new_name()
                                self.session.add(current_table_data)
                                self.session.flush()
                            else:
                                current_inst_name = fields['name_' + str(row_id)]
                        else:
                            current_inst_name = fields['name_' + str(row_id)]

                        fields['name_' + str(row_id)] = current_inst_name
                    else:
                        instances[row_id] = self.session.query(current_table_object). \
                            filter_by(name=current_inst_name).first()

                        if old_fields['date_created_' + str(row_id)] == '':
                            setattr(instances[row_id], 'date_created', datetime.datetime.utcnow())

                    setattr(instances[row_id], 'last_modified', datetime.datetime.utcnow())

                if field_data[table_id_field][column_name].Field.foreign_key_table_object_id == long_text_data.id and \
                                data != '':
                    if old_fields[field_id] == '':
                        lt = core_models.LongText()
                        setattr(lt, 'name', long_text_data.get_new_name())
                        setattr(lt, 'date_created', datetime.datetime.utcnow())
                    else:
                        lt_id = old_fields[field_id]
                        lt = self.session.query(core_models.LongText).filter_by(id=lt_id).first()

                    setattr(lt, 'organization_id', row_org_id[row_id])
                    setattr(lt, 'last_modified', datetime.datetime.utcnow())
                    setattr(lt, 'long_text', data)
                    self.session.add(lt)
                    self.session.flush()
                    lt_id = lt.id
                    setattr(instances[row_id], column_name, lt_id)
                elif field_data[table_id_field][column_name].Field.foreign_key_table_object_id is not None:
                    try:
                        # TODO find a better way to deal with no value in a select
                        # a top row is is added to all selects with an index of -99 (get_foreign_key_data)
                        if int(data) == -99:
                            setattr(instances[row_id], column_name, None)
                        else:
                            setattr(instances[row_id], column_name, int(data))
                    except ValueError:
                        if field_data[table_id_field][column_name].Field.foreign_key_display is None:
                            fk_display = 'name'
                        else:
                            fk_display = field_data[table_id_field][column_name].Field.foreign_key_display

                        fk_id = []
                        if data is not None and data != '':
                            fk_id = self.get_foreign_key_data(field_data[table_id_field][column_name].\
                                                              Field.foreign_key_table_object_id,
                                                              {fk_display: data})

                        if len(fk_id) > 1:
                            setattr(instances[row_id], column_name, fk_id[1][0])
                            data = fk_id[1][0]
                        else:
                            setattr(instances[row_id], column_name, None)
                elif column_name != 'id' and column_name != 'last_modified' and column_name != 'date_created':
                    if field_data[table_id_field][column_name].Field.data_type_id == 1:
                        if data is None or data == '':
                            setattr(instances[row_id], column_name, None)
                        else:
                            setattr(instances[row_id], column_name, int(data))
                    elif field_data[table_id_field][column_name].Field.data_type_id == 8:
                        if data is None or data == '':
                            setattr(instances[row_id], column_name, None)
                        else:
                            setattr(instances[row_id], column_name, float(data))
                    elif field_data[table_id_field][column_name].Field.data_type_id == 3:
                        if data == 'y':
                            setattr(instances[row_id], column_name, 1)
                            data = True
                        else:
                            setattr(instances[row_id], column_name, 0)
                            data = False
                    else:
                        setattr(instances[row_id], column_name, data)

                if column_name != 'last_modified' and column_name != 'date_created' and \
                        not (old_fields[field_id] == data or old_fields[field_id] == str(data)):
                    history_instance = core_models.History()
                    history_instance.name = history_data.get_new_name()
                    history_instance.date_created = datetime.datetime.utcnow()
                    history_instance.last_modified = datetime.datetime.utcnow()
                    history_instance.table_object_id = table_id_field
                    history_instance.field_id = field_data[table_id_field][column_name].Field.id
                    history_instance.organization_id = row_org_id[row_id]
                    history_instance.user_id = g.user.id
                    history_instance.instance_name = current_inst_name
                    history_instance.old_value = old_fields[field_id]
                    history_instance.new_value = data
                    self.session.add(history_instance)
                    self.session.flush

            self.session.add(history_data)
            self.session.flush()

            row_names = []
            for row_id, instance in instances.items():
                self.session.add(instance)
                self.session.flush()
                row_names.append([instance.name, instance.__tablename__])

            self.session.commit()
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

        rows = self.session.query(child_table).filter(getattr(child_table, field.field_name) == parent_id).all( )

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
            else:
                self.session.rollback()
        return updated
