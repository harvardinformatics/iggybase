from flask import g, request
from iggybase.mod_auth.role_access_control import RoleAccessControl
from iggybase.database import db_session
from iggybase.mod_admin import models
from iggybase import models as core_models
from iggybase.mod_core import utilities as util
from sqlalchemy.orm import aliased
import datetime
import logging


# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__(self):
        self.org_ids = []
        if g.user is not None and not g.user.is_anonymous:
            self.user = models.load_user(g.user.id)
            user_orgs = db_session.query(models.UserOrganization).filter_by(user_id=self.user.id).all()

            for user_org in user_orgs:
                self.get_child_organization(user_org.user_organization_id)
                if user_org.default_organization:
                    self.current_org_id = user_org.user_organization_id
        else:
            self.user = None
            self.current_org_id = None

    def get_child_organization(self, parent_organization_id):
        self.org_ids.append(parent_organization_id)
        child_orgs = db_session.query(models.Organization).filter_by(parent_id=parent_organization_id).all()

        if child_orgs is None:
            return

        for child_org in child_orgs:
            self.get_child_organization(child_org.id)

        return

    def get_entry_data(self, module, table_name, name=None):
        field_data = self.get_field_data(module, table_name)
        results = None

        if field_data is not None:
            table_object = util.get_table(table_name)

            columns = []
            for row in field_data:
                if row.FieldRole.visible == 1:
                    columns.append(getattr(table_object, row.Field.field_name). \
                                   label(row.FieldRole.display_name))

            criteria = [getattr(table_object, 'organization_id').in_(self.org_ids)]

            if name is not None:
                criteria.append(getattr(table_object, 'name') == name)

            results = db_session.query(*columns).filter(*criteria).all()

        return results

    def get_foreign_key_data(self, fk_table_id, column_value=None):
        fk_table_data = db_session.query(models.TableObject).filter_by(id=fk_table_id).first()
        fk_field_data = self.foreign_key(fk_table_id)

        results = [(-99, '')]

        if fk_field_data is not None:
            fk_table_object = util.get_table(fk_table_data.name)

            if column_value is None:
                rows = fk_field_data['fk_session'].query(getattr(fk_table_object, 'id'),
                                                         getattr(fk_table_object, 'name')).all()
            else:
                rows = fk_field_data['fk_session'].query(getattr(fk_table_object, 'id'),
                                                         getattr(fk_table_object, 'name')). \
                    filter(getattr(fk_table_object, 'name') == column_value).all()

            for row in rows:
                results.append((row.id, row.name))

        return results

    def get_table_query_data(self, table_fields, criteria={}):
        results = []
        tables = set([])
        joins = set([])
        outer_joins = []
        columns = []
        fk_columns = []
        aliases = {}
        wheres = []
        first_table_named = None  # set to first table name, dont add to joins
        for row in table_fields:
            table_model = util.get_table(row.TableObject.name)
            tables.add(table_model)
            field_display_name = util.get_field_attr(row.TableQueryField, row.Field, 'display_name')
            if row.Field.foreign_key_table_object_id is not None:  # fk field
                # get fk data so we can include name and form url link
                fk_data = self.foreign_key(row.Field.foreign_key_table_object_id)
                # create alias to the fk table
                # solves the case of more than one join to same table
                alias_name = row.TableObject.name + '_' + row.Field.field_name + '_' + fk_data['name']
                aliases[alias_name] = aliased(util.get_table(fk_data['name']))
                outer_joins.append((
                    aliases[alias_name],
                    getattr(table_model, row.Field.field_name) == aliases[alias_name].id
                ))
                columns.append(getattr(aliases[alias_name], fk_data['foreign_key']).
                    label(
                        'fk|' + fk_data['url_prefix']
                        + '|' + fk_data['name']
                        + '|' + field_display_name)
                )
                criteria_key = (fk_data['name'], fk_data['foreign_key'])
                if criteria_key in criteria:
                    wheres.append(getattr(aliases[alias_name],
                                          fk_data['foreign_key']) == criteria[criteria_key])

            else:  # non-fk field
                col = getattr(table_model, row.Field.field_name)
                columns.append(col.label(field_display_name))
                criteria_key = (row.TableObject.name, row.Field.field_name)
                if criteria_key in criteria:
                    wheres.append(col == criteria[criteria_key])
                # add to joins if not first table, avoid joining to self
                if (not first_table_named
                    or (first_table_named == row.TableObject.name)):
                    first_table_named = row.TableObject.name
                else:
                    joins.add(table_model)
        # add organization id checks on all tables, does not include fk tables
        for table_model in tables:
            wheres.append(getattr(table_model, 'organization_id').in_(self.org_ids))
        results = (
            db_session.query(*columns).
                join(*joins).
                outerjoin(*outer_joins).
                filter(*wheres).all()
        )
        return results

    def foreign_key(self, table_object_id):
        res = (db_session.query(models.Field, models.TableObject, models.Module).
               join(models.TableObject,
                    models.TableObject.id == models.Field.table_object_id
                    ).
               join(models.TableObjectRole).
               join(models.Module).
               filter(models.Field.table_object_id == table_object_id).
               filter(models.Field.field_name == 'name').first())

        if res.Module.name == 'mod_admin':
            fk_session = db_session
        else:
            fk_session = db_session

        return {'foreign_key': res.Field.field_name,
                'module': res.Module.name,
                'url_prefix': res.Module.url_prefix,
                'name': res.TableObject.name,
                'fk_session': fk_session
                }

    def get_field_data(self, module, table_name):
        role_access_control = RoleAccessControl()
        table_data = role_access_control.has_access('TableObject', {'name': table_name})
        field_data = None

        if table_data is not None:
            field_data = role_access_control.fields(table_data.id, module)

        return field_data

    def get_search_field_data(self, module, table_name, search_field_name):
        role_access_control = RoleAccessControl()
        table_data = role_access_control.has_access('TableObject', {'name': table_name})

        if table_data is not None:
            field_data = role_access_control.fields(table_data.id, module,
                                                    {'field.field_name': search_field_name})

            if field_data is not None:
                search_table = role_access_control.has_access('TableObject',
                                                              {'id': field_data[0].Field.foreign_key_table_object_id})

                if search_table is not None:
                    search_table_data = self.foreign_key(search_table.id)
                    search_field_data = role_access_control.fields(search_table.id,
                                                                   search_table_data['module'],
                                                                   {'field_role.search_field': 1})

                    return search_table_data['module'], search_table_data['name'], search_field_data

        return None, None, None

    def get_search_results(self, module, table_name, params):
        table = util.get_table(table_name)
        filters = []
        for key, value in params.items():
            filters.append((getattr(table, key)).like('%' + value + '%'))
        return table.query.filter(*filters).order_by(getattr(table, 'name'))

    def get_long_text(self, lt_id):
        table = util.get_table("long_text")

        return table.query.filter_by(id=lt_id).first()

    def save_form(self, form):
        role_access_control = RoleAccessControl()
        table_object = util.get_table(form.table_object_0.data)
        table_object_data = models.TableObject.query.filter_by(name=table_object.__tablename__).first()
        table_record = models.TableObjectName.query.filter_by(table_object_id=table_object_data.id). \
            filter_by(facility_id=role_access_control.role.facility_id).first()

        long_text_data = models.TableObject.query.filter_by(name='long_text').first()
        long_text_record = models.TableObjectName.query.filter_by(table_object_id=long_text_data.id). \
            filter_by(facility_id=role_access_control.role.facility_id).first()

        history_data = models.TableObject.query.filter_by(name='history').first()
        history_record = models.TableObjectName.query.filter_by(table_object_id=history_data.id). \
            filter_by(facility_id=role_access_control.role.facility_id).first()

        hidden_fields = {}
        child_tables = {}
        child_record_tables = {}
        form_fields = {}
        last_row_id = 0
        instances = {}
        prefix = ''
        for field in form:
            if field.name.endswith('_token'):
                continue
            elif field.name.endswith('_0'):
                form_fields[field.name[:field.name.index('_')]] = field.data
                continue
            elif field.name.startswith('hidden_'):
                field_id = field.name[field.name.index('_') + 1:]
                hidden_fields[field_id] = field.data
                continue
            elif field.name.startswith('child_'):
                prefix = 'child_'
                field_id = field.name[field.name.index('_') + 1:]
                row_id = int(field_id[field_id.rindex('_') + 1:])
                column_name = field_id[:field_id.rindex('_')]

                if field['child_table_id_' + str(row_id)] not in child_tables.keys():
                    child_tables[field['child_table_id_' + str(row_id)]] = util.get_table(
                            field['child_table_id_' + str(row_id)])

                    child_table_object_data = models.TableObject.query.\
                        filter_by(name=child_tables[field['child_table_id_' + str(row_id)]].__tablename__).first()

                    child_record_tables[field['child_table_id_' + str(row_id)]] = models.TableObjectName.query.\
                        filter_by(table_object_id=child_table_object_data.id). \
                        filter_by(facility_id=role_access_control.role.facility_id).first()

                current_table_object = child_tables[field['child_table_id_' + str(row_id)]]
                current_table_record = child_record_tables[field['child_table_id_' + str(row_id)]]

            else:
                current_table_object = table_object
                current_table_record = table_record

                field_id = field.name
                row_id = int(field_id[field_id.rindex('_') + 1:])
                column_name = field_id[:field_id.rindex('_')]

            field_data = role_access_control.fields(int(hidden_fields['table_id_' + str(row_id)]),
                                                    form.module_0.data, {'field.field_name': column_name})[0]

            if last_row_id != row_id and row_id not in instances:
                if hidden_fields['row_name_' + str(row_id)] == 'new':
                    name_field = getattr(form, prefix + 'name_' + str(row_id))
                    instances[row_id] = current_table_object()
                    setattr(instances[row_id], 'date_created', datetime.datetime.utcnow())
                    setattr(instances[row_id], 'organization_id', self.current_org_id)
                    if current_table_record.new_name_prefix is not None and current_table_record.new_name_prefix != "":
                        current_inst_name = current_table_record.get_new_name()
                        setattr(instances[row_id], 'name', current_inst_name)
                        db_session.add(current_table_record)
                        db_session.commit()

                    if name_field.data != '':
                        current_inst_name = name_field.data
                else:
                    current_inst_name = hidden_fields['row_name_' + str(row_id)]
                    instances[row_id] = db_session.query(current_table_object). \
                        filter_by(name=current_inst_name).first()

                setattr(instances[row_id], 'last_modified', datetime.datetime.utcnow())

            if not (hidden_fields[field_id] == field.data or hidden_fields[field_id] == str(field.data)):
                history_instance = core_models.History()
                history_instance.name = history_record.get_new_name()
                history_instance.table_object_id = hidden_fields['table_id_' + str(row_id)]
                history_instance.field_id = field_data.Field.id
                history_instance.organization_id = self.current_org_id
                history_instance.user_id = g.user.id
                history_instance.instance_name = current_inst_name
                history_instance.old_value = hidden_fields[field_id]
                history_instance.new_value = field.data
                db_session().add(history_instance)

            if field_data.Field.foreign_key_table_object_id is not None and not isinstance(field.data, int):
                fk_id = self.get_foreign_key_data(field_data.Field.foreign_key_table_object_id, field.data)
                if len(fk_id) > 1:
                    setattr(instances[row_id], column_name, fk_id[1][0])
                else:
                    setattr(instances[row_id], column_name, None)
            elif field_data.Field.data_type_id == 7 and field.data != '':
                if hidden_fields[field_id] == '':
                    lt = core_models.LongText()
                    db_session().add(lt)
                    db_session().flush
                    lt_id = lt.id

                    setattr(lt, 'name', long_text_record.get_new_name())
                    db_session.add(long_text_record)

                    setattr(lt, 'date_created', datetime.datetime.utcnow())
                    setattr(lt, 'organization_id', self.current_org_id)
                else:
                    lt_id = hidden_fields[field_id]
                    lt = db_session.query(core_models.LongText).filter_by(id=lt_id).first()

                setattr(lt, 'last_modified', datetime.datetime.utcnow())
                setattr(lt, 'long_text', field.data)
                db_session().add(lt)
                setattr(instances[row_id], column_name, lt_id)
            else:
                setattr(instances[row_id], column_name, field.data)

        row_names = []

        for row_id, instance in instances.items():
            db_session().add(instance)
            db_session().flush()
            row_names.append(instance.name)

        try:
            db_session.commit()
            return row_names
        except:
            db_session.rollback()
            raise

    def get_child_row_names(self, child_table_name, child_link_field_id, parent_id):
        field = db_session.query(models.Field).filter_by(id=child_link_field_id).first()

        child_table = util.get_table(child_table_name)

        rows = db_session.query(child_table).filter(getattr(child_table, field.field_name) == parent_id).all( )

        names = []
        for row in rows:
            names.append(row.nome)

        return names

    def update_table_rows(self, table, updates, ids):
        # TODO: make this deal with foreign keys
        # for now i'm just going to pass in the numeric value
        table_model = util.get_table(table)
        rows = table_model.query.filter(table_model.id.in_(ids), getattr(table_model, 'organization_id').in_(self.org_ids)).all()
        for row in rows:
            for col, val in updates.items():
                try:
                    setattr(row, col, val)
                    db_session.commit()
                except AttributeError:
                    pass
        return True
