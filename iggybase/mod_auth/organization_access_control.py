from flask import g, request
from iggybase.database import db_session
from iggybase.mod_auth.models import load_user, UserRole, Organization
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
from importlib import import_module
from iggybase.database import admin_db_session
from iggybase.mod_admin import models
#from iggybase.mod_core.models import History
from iggybase.tablefactory import TableFactory
from sqlalchemy.orm import joinedload, aliased
import datetime
import logging

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__(self, module):
        self.org_ids = []
        self.tables = []
        #TODO: remove module from calls to init
        self.module, self.page_form = request.endpoint.split('.')

        if g.user is not None and not g.user.is_anonymous:
            self.user = load_user(g.user.id)
            self.user_role = db_session.query(UserRole).filter_by(id=self.user.current_user_role_id).first()
            self.facility_role_access_control = FacilityRoleAccessControl()
            self.current_org_id = self.user_role.organization_id

            self.get_child_organization(self.user_role.organization_id)
        else:
            self.user = None
            self.user_role = None
            self.current_org_id = None

    def get_child_organization(self, parent_organization_id):
        self.org_ids.append(parent_organization_id)

        child_orgs = db_session.query(Organization).filter_by(parent_id=parent_organization_id).all()

        if child_orgs is None:
            return

        for child_org in child_orgs:
            self.get_child_organization(child_org.id)

        return

    def get_entry_data(self, table_name, name=None):
        field_data = self.get_field_data(table_name)

        results = None

        if field_data is not None:
            module_model = import_module('iggybase.' + self.module + '.models')
            table_object = getattr(module_model, table_name)

            columns = []
            for row in field_data:
                if row.FieldFacilityRole.visible == 1:
                    columns.append(getattr(table_object, row.Field.field_name). \
                                   label(row.FieldFacilityRole.display_name))

            criteria = [getattr(table_object, 'organization_id').in_(self.org_ids)]

            if name is not None:
                criteria.append(getattr(table_object, 'name') == name)

            results = db_session.query(*columns). \
                filter(*criteria).all()

        return results

    def get_lookup_data(self, fk_table_id):
        fk_table_data = admin_db_session.query(models.TableObject).filter_by(id=fk_table_id).first()
        fk_table_name = TableFactory.to_camel_case(fk_table_data.name)
        fk_field_data = self.foreign_key(fk_table_id)

        results = [(-99, '')]

        if fk_field_data is not None:
            fk_module_model = import_module('iggybase.' + fk_field_data['module'] + '.models')
            fk_table_object = getattr(fk_module_model, fk_table_name)

            rows = db_session.query(getattr(fk_table_object, 'id'), getattr(fk_table_object, 'name')).all()

            for row in rows:
                results.append((row.id, row.name))

        return results

    def get_summary_data(self, table_name, query_data={}):
        self.tables = []
        field_data = self.get_field_data(table_name)

        results = None

        if field_data is not None:
            module_model = import_module('iggybase.' + self.module + '.models')
            table_object = getattr(module_model, TableFactory.to_camel_case(table_name))

            self.table_object = table_object
            self.tables.append(table_object)
            qry = db_session.query(table_object)
            columns = []
            joins = []
            criteria = []

            for row in field_data:
                if row.FieldFacilityRole.visible == 1:
                    if row.Field.foreign_key_table_object_id is not None:
                        fk_table_data = admin_db_session.query(models.TableObject). \
                            filter_by(id=row.Field.foreign_key_table_object_id).first()
                        fk_table_name = TableFactory.to_camel_case(fk_table_data.name)
                        foreign_key_data = self.foreign_key(row.Field.foreign_key_table_object_id)

                        module_model = import_module('iggybase.' + foreign_key_data['module'] + '.models')
                        fk_table_object = getattr(module_model, fk_table_name)
                        self.tables.append(fk_table_object)
                        joins.append(joinedload(getattr(table_object, table_object.__tablename__ + '_' + fk_table_data.name)))
                        criteria.append(getattr(fk_table_object, 'organization_id').in_(self.org_ids))

                        columns.append(getattr(table_object, row.Field.field_name).
                                       label('fk|' + fk_table_name + '|id'))

                        columns.append(getattr(fk_table_object, foreign_key_data['foreign_key']).
                                       label('fk|' + foreign_key_data['url_prefix'] + '|' + fk_table_name + '|' +
                                             foreign_key_data['foreign_key_alias']))
                    else:
                        columns.append(getattr(table_object, row.Field.field_name).
                                       label(row.FieldFacilityRole.display_name))

            criteria.append(getattr(table_object, 'organization_id').in_(self.org_ids))
            if 'criteria' in query_data:
                for col, value in query_data['criteria'].items():
                    criteria.append(getattr(table_object, col) == value)

            if not joins:
                results = db_session.query(self.tables[0]).add_columns(*columns).filter(*criteria).all()
            else:
                results = db_session.query(self.tables[0]).add_columns(*columns).options(*joins). \
                    filter(*criteria).all()

        return results

    def get_summary_data2(self, table_name, query_data={}):
        """TODO: replace original once every endpoint is using table_query, only
        change is to call get_field_data2
        """
        self.tables = []
        field_data = self.get_field_data2(table_name)
        table_name = table_name
        results = None
        if field_data is not None:
            module_model = import_module('iggybase.' + self.module + '.models')
            table_object = getattr(module_model, TableFactory.to_camel_case(table_name))

            self.table_object = table_object
            self.tables.append(table_object)
            qry = db_session.query(table_object)
            columns = []
            joins = []
            criteria = []

            for row in field_data:
                if row.FieldFacilityRole.visible == 1:
                    if row.Field.foreign_key_table_object_id is not None:
                        fk_table_data = admin_db_session.query(models.TableObject). \
                            filter_by(id=row.Field.foreign_key_table_object_id).first()
                        fk_table_name = TableFactory.to_camel_case(fk_table_data.name)
                        foreign_key_data = self.foreign_key(row.Field.foreign_key_table_object_id)

                        module_model = import_module('iggybase.' + foreign_key_data['module'] + '.models')
                        fk_table_object = getattr(module_model, fk_table_name)
                        self.tables.append(fk_table_object)
                        joins.append(joinedload(getattr(table_object, table_object.__tablename__ + '_' + fk_table_data.name)))
                        criteria.append(getattr(fk_table_object, 'organization_id').in_(self.org_ids))

                        columns.append(getattr(table_object, row.Field.field_name).
                                       label('fk|' + fk_table_name + '|id'))

                        columns.append(getattr(fk_table_object, foreign_key_data['foreign_key']).
                                       label('fk|' + foreign_key_data['url_prefix'] + '|' + fk_table_name + '|' +
                                             foreign_key_data['foreign_key_alias']))
                    else:
                        columns.append(getattr(table_object, row.Field.field_name).
                                       label(row.FieldFacilityRole.display_name))

            criteria.append(getattr(table_object, 'organization_id').in_(self.org_ids))
            if 'criteria' in query_data:
                for col, value in query_data['criteria'].items():
                    criteria.append(getattr(table_object, col) == value)

            # TODO: order the results by order in the table_query_field table
            if not joins:
                results = db_session.query(self.tables[0]).add_columns(*columns).filter(*criteria).all()
            else:
                results = db_session.query(self.tables[0]).add_columns(*columns).options(*joins). \
                    filter(*criteria).all()

        return results
    def format_data(self, results, for_download = False):
        """Formats data for summary or detail
        - transforms into dictionary
        - removes model objects sqlalchemy puts in
        - formats FK data and link
        - formats name link which goes to detail template
        """
        table_rows = []
        # format results as dictionary
        if results:
            keys = results[0].keys()
            # filter out any objects
            keys_to_skip = []
            for fk in self.tables:
                keys_to_skip.append(fk.__name__)
            # create dictionary for each row and for fk data
            for row in results:
                row_dict = {}
                for i, col in enumerate(row):
                    if keys[i] not in keys_to_skip:
                        if 'fk|' in keys[i]:
                            if '|name' in keys[i]:
                                fk_metadata = keys[i].split('|')
                                if fk_metadata[2]:
                                    table = fk_metadata[2]
                                    if for_download:
                                        item_value = col
                                    else:
                                        item_value = {
                                            'text': col,
                                            # add link foreign key table summary
                                            'link': '/' + fk_metadata[1] \
                                                    + '/detail/' + table + '/' \
                                                    + str(col)
                                        }
                                    row_dict[table] = item_value
                        else:  # add all other colums to table_rows
                            if for_download:
                                item_value = col
                            else:
                                item_value = {'text': col}
                            row_dict[keys[i]] = item_value
                            # name column values will link to detail
                            if keys[i] == 'name' and not for_download:
                                row_dict[keys[i]]['link'] = '/' \
                                                            + self.module.replace('mod_', '') + '/detail/' \
                                                            + self.table_object.__name__ + '/' + str(col)
                table_rows.append(row_dict)
        return table_rows

    def foreign_key(self, table_object_id):
        res = admin_db_session.query(models.Field, models.FieldFacilityRole, models.Module). \
            join(models.FieldFacilityRole). \
            join(models.Module). \
            filter(models.Field.table_object_id == table_object_id). \
            filter(models.Field.field_name == 'name'). \
            order_by(models.FieldFacilityRole.order, models.FieldFacilityRole.id).first()

        return {'foreign_key':res.Field.field_name, 'foreign_key_alias':res.FieldFacilityRole.display_name,
                'module':res.Module.name, 'url_prefix':res.Module.url_prefix}

    def get_field_data(self, table_name):
        table_data = self.facility_role_access_control.has_access('TableObject', table_name)

        field_data = None

        if table_data is not None:
            field_data = self.facility_role_access_control.fields(table_data.id, self.module)

        return field_data

    def get_field_data2(self, table_name):
        """TODO: replace original once every endpoint is using table_query
        """
        table_data = self.facility_role_access_control.has_access('TableObject', table_name)

        field_data = None

        if table_data is not None:
            table_queries = self.get_table_queries(table_name)
            field_data = self.facility_role_access_control.fields2(table_queries[0].id, self.module)
        return field_data

    def save_form(self, form):
        session = db_session()
        module_model = import_module('iggybase.' + form.model_0.data + '.models')
        table_object = getattr( module_model, form.table_object_0.data )
        if form.entry_0.data == 'parent_child':
            child_table_object = getattr( module_model, form.chile_table_object_0.data )

        hidden_fields={}
        last_row_id=1
        new_instance=table_object()
        for field in form:
            if field.name.endswith('_0'):
                continue
            elif field.name.startswith('hidden_'):
                field_id = field.name[field.name.index('_'):]
                hidden_fields[field_id]=field.data
                continue
            elif field.name.beginswith('child_'):
                field_id = field.name[field.name.index('_'):]
                current_table_object = child_table_object
            else:
                field_id = field.name
                current_table_object = table_object

            row_id = int(field_id[field_id.index('_'):])
            column_name = int(field_id[:field_id.index('_')])

            if last_row_id != row_id:
                session.add(new_instance)
                session.commit()

                new_instance = current_table_object()
                new_instance.last_modified=datetime.datetime.utcnow()

                if hidden_fields['name_'+str(row_id)] == 'new':
                    new_instance.date_created=datetime.datetime.utcnow()
                    new_instance.organization_id=self.current_org_id

            #if hidden_fields[field_id]!=field.data:
            #    history_instance=History()

            column_to_update=getattr(new_instance, column_name)

            column_to_update=field.data

        session.add(new_instance)
        session.commit()

    def get_additional_tables( self, table_name, page_form = 'detail'):
        """Get additional tables that need to be displayed on the page
        """
        to_page = aliased(models.TableObject)
        to_additional = aliased(models.TableObject)
        # fetch the names of tables we need to display for this page and obejct
        table_queries = admin_db_session.query(models.TableQuery.id, to_additional.name).\
                join(models.TableQueryTableObject).\
                join(to_page, to_page.id ==
                        models.TableQueryTableObject.table_object_id).\
                join(to_additional, to_additional.id ==
                        models.TableQuery.table_object_id).\
                join(models.TableQueryPageForm).\
                join(models.PageForm).\
                filter(models.PageForm.name == page_form, to_page.name == table_name.lower()).\
                filter(to_page.name != to_additional.name).all()
        # get the summary data for these tables
        additional_tables = []
        for row in table_queries:
            #TODO: should routes call this to be consistant?
            results = self.get_summary_data2(row.name)
            additional_tables.append(results)

        return additional_tables

    def get_table_queries( self, table_name):
        """Get the table query to use
        """
        table_queries = admin_db_session.query(models.TableQuery.id,
                models.TableObject.name).\
                join(models.TableQueryTableObject).\
                join(models.TableObject, models.TableObject.id ==
                        models.TableQuery.table_object_id).\
                join(models.TableQueryPageForm).\
                join(models.PageForm).\
                filter(models.PageForm.name == self.page_form, models.TableObject.name == table_name.lower()).all()
        return table_queries
