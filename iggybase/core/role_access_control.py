from collections import OrderedDict as OrderedDict
from flask import g, request, session, current_app
import json
from iggybase.database import db_session
from iggybase.admin import models
from iggybase.admin import constants as admin_consts
from iggybase import utilities as util
from sqlalchemy import or_, and_, distinct
from sqlalchemy.orm import aliased
import logging
from sqlalchemy.dialects import mysql

# Controls access to system based on oole (USER) and Facility
# Uses the permissions stored in the admin db
class RoleAccessControl:
    def __init__(self):
        self.session = db_session()
        # set user and role
        if (g.user is not None and not g.user.is_anonymous):
            self.user = self.session.query(models.User).filter_by(id=g.user.id).first()

            if self.user.current_user_role_id is None:
                role_data = (self.session.query(models.Role, models.UserRole)
                             .join(models.UserRole)
                             .filter(models.UserRole.user_id==self.user.id).first())

                if role_data is None:
                    self.user = None
                    self.role = None
                    return

                self.user.current_user_role_id =  role_data.UserRole.id
                self.session.add(self.user)
                self.session.commit()
                self.role = role_data.Role
            else:
                self.role = (self.session.query(models.Role)
                             .join(models.UserRole)
                             .filter(models.UserRole.id==self.user.current_user_role_id).first())

            g.role_id = self.role.id
            facility_res = (self.session.query(models.Facility, models.Role,
                                               models.Level)
                            .join(models.Role, models.UserRole,
                                  models.Level)
                            .filter(models.UserRole.user_id ==
                                    self.user.id).order_by(models.Facility.id,
                                                           models.Level.order).all())

            self.facilities = {}
            self.facility = None
            self.level_id = None
            for fac in facility_res:
                if fac.Facility.name not in self.facilities:
                    self.facilities[fac.Facility.name] = {'top_role':fac.Role.id, 'roles': []}
                self.facilities[fac.Facility.name]['roles'].append(fac.Role.id)
                if fac.Role.id == self.role.id:
                    self.facility = fac.Facility
                    self.level_id = fac.Role.level_id
                    g.root_org_id = fac.Facility.root_organization_id

            # if set_routes is a url param then set_routes
            filters = util.get_filters()
            if 'set_routes' not in filters and 'routes' in session and session['routes']:
                self.routes = session['routes']
            else:
                self.set_routes()
                logging.info('routes set for user: ' + self.user.name + ' routes: ' + json.dumps(self.routes))
        else:
            self.user = None
            self.role = None
            self.routes = []
            self.level_id = None
            self.facility = None

    def __del__(self):
        self.session.rollback()

    def table_queries(self, route, table_name=None, active=1):
        """Get the table queries
        """
        filters = [
            (models.Route.url_path == route),
            (models.RouteRole.role_id == self.role.id),
            (models.TableQuery.active == active)
        ]
        if table_name:
            filters.append(
                (models.TableQueryRender.dynamic_field == table_name)
            )

        table_queries = (
            self.session.query(
                models.TableQueryRender,
                models.TableQuery
            ).
                join(models.RouteRole).
                join(models.Route).
                join(models.TableQuery).
                filter(*filters).order_by(models.TableQuery.order).all()
        )
        return table_queries

    def calculation_fields(self, table_query_calculation_id, active=1):
        filters = [
            (models.FieldRole.role_id == self.role.id),
            (models.TableObjectRole.role_id == self.role.id),
            (models.Field.active == active),
            (models.FieldRole.active == active),
            (models.TableObject.active == active),
            (models.TableQueryCalculationField.table_query_calculation_id == table_query_calculation_id)
        ]
        joins = [
            models.FieldRole,
            models.TableObjectRole,
        ]

        res = (
            self.session.query(models.TableQueryCalculationField,
                               models.TableQueryField, models.Field,
                               models.TableObject).
                join(models.TableQueryField).
                join(models.Field).
                join(
                models.TableObject,
                models.TableObject.id == models.Field.table_object_id
            ).
                join(*joins).
                filter(*filters).order_by(models.TableQueryCalculationField.order).all()
        )
        return res

    def table_query_fields(self, table_query_id, table_names=None, table_id=None, criteria = {}, role_filter = True, active=1):
        filters = [
            (models.Field.active == active),
            (models.FieldRole.active == active),
            (models.TableObject.active == active),
            (models.Field.data_type_id == models.DataType.id)
        ]

        # filters not needed for name of fk_field
        # That means we get many rows for fk_field that are all the same and
        # just use the first one
        if role_filter:
            filters.append((models.TableObjectRole.role_id == self.role.id))
            filters.append((models.FieldRole.role_id == self.role.id))

        selects = [
            models.Field,
            models.TableObject,
            models.FieldRole,
            models.TableObjectRole,
            models.DataType
        ]
        joins = [
            models.FieldRole,
            (models.TableObject,
            models.TableObject.id == models.Field.table_object_id),
            models.TableObjectRole,
            models.DataType
        ]
        orders = [
            models.FieldRole.order,
            models.Field.order,
            models.FieldRole.display_name,
            models.Field.display_name
        ]
        outerjoins = []

        # aliased TableObject for extends tables
        extension = aliased(models.TableObject, name='extension')
        # add filter for the identifier
        if table_query_id:
            filters.append((models.TableQueryField.table_query_id == table_query_id))
            filters.append((models.TableQueryField.active == active))
            selects.append(models.TableQueryField)
            selects.append(models.TableQueryCalculation)
            joins.append(models.TableQueryField)
            outerjoins.append(models.TableQueryCalculation)
            # must find table_names as filter for extension query
            # else we would have multiple rows due to multiple extensions
            tbl_names = (self.session.query(distinct(models.TableObject.name))
                    .join((models.Field, models.TableObject.id ==
                        models.Field.table_object_id), models.TableQueryField)
                    .filter(models.TableQueryField.table_query_id == table_query_id).all())
            tbls = [r[0] for r in tbl_names]
            extends_join = (extension.name.in_(tbls))
            outerjoins.append((extension, and_(extension.extends_table_object_id == models.TableObject.id, extends_join)))
            orders = [
                models.TableQueryField.order,
                models.Field.order
            ]
        else:
            if table_names:
                filters.append((models.TableObject.name.in_(table_names)))
                extends_join = (extension.name.in_(table_names))
            elif table_id:
                filters.append((models.TableObject.id == table_id))
                extends_join = (extension.id == table_id)
            outerjoins.append((extension, and_(extension.extends_table_object_id == models.TableObject.id, extends_join)))
        selects.append(extension)

        # add any field_name filter
        if criteria:
            for key, val in criteria.items():
                crit_field = getattr(models.Field, key, None)
                if crit_field:
                    filters.append((crit_field == val))
        res = (
            self.session.query(*selects).
                join(*joins).
                outerjoin(*outerjoins).
                filter(*filters).order_by(*orders)
        ).all()
        return res

    def table_query_criteria(self, table_query_id):
        criteria = (
            self.session.query(
                models.TableQueryCriteria,
                models.Field,
                models.TableObject
            ).join(
                models.Field
            ).join(
                (models.TableObject, models.Field.table_object_id ==
                 models.TableObject.id)
            ).join(
                models.TableObjectRole
            ).
                filter(models.TableQueryCriteria.table_query_id == table_query_id).all()
        )
        return criteria

    def set_routes(self):
        self.routes = {}
        res = (self.session.query(models.Route, models.RouteRole, models.Module,
            models.ModuleFacility)
                .join(models.RouteRole, models.Route.id==models.RouteRole.route_id)
                .join(models.Module, models.Route.module_id==models.Module.id)
                .join(models.ModuleFacility, models.Module.id==models.ModuleFacility.module_id)
        .filter(
            models.RouteRole.role_id == self.role.id,
            models.RouteRole.active == 1,
            models.ModuleFacility.facility_id == self.facility.id
        ).all())
        rules = {}
        for rule in current_app.url_map._rules:
            rules[rule.endpoint] = list(rule.arguments)
        for row in res:
            path =  self.facility.name + '/' + row.Module.name + '/' + row.Route.url_path
            endpoint = row.Module.name + '.' + row.Route.url_path
            args = []
            if endpoint in rules:
                args = rules[endpoint]
            self.routes[endpoint] = args
        session['routes'] = self.routes

    def route_access(self, route):
        route = route.strip('/')
        route = route.split('/')
        route = '.'.join(route[1:3])
        if route in self.routes:
            return True
        else:
            logging.info(
                'user: '
                + g.user.name
                + ' has no access to this route: '
                + route
            )
            return False

    def get_menu(self, name, active=True):
        """Setup NavBar and Side bar menus for templating context.
        Starts with the root navbar and sidebar records.
        Menus are recursive.
        """
        menu_root = self.session.query(models.Menu). \
            filter_by(name=name).first()
        return menu_root

    def make_user_menu(self):
        subs = {}
        if 'core.change_user' in self.routes:
            user_menu_subs = OrderedDict()
            roles = self.facilities[self.facility.name]['roles']
            if roles is not None:
                users = (self.session.query(models.User)
                        .join(models.UserRole, models.User.id ==
                            models.UserRole.user_id)
                .filter(models.UserRole.role_id.in_(roles), models.User.active == 1, models.UserRole.active == 1).all())
                for user in users:
                    user_menu_subs[user.name] = {'title': user.name,
                                                    'class': 'change_user',
                                                    'data': {'user_id': user.id}}
            if user_menu_subs:
                subs = {'title': 'Change User',
                        'subs': user_menu_subs}
        return subs

    def make_role_menu(self):
        role_menu_subs = OrderedDict({})
        if self.user is not None:
            for user_role in self.user.user_roles:
                if user_role.role_id != self.role.id and user_role.active == 1 and user_role.role.active == 1:
                    facility = self.session.query(models.Facility).filter_by(id=user_role.role.facility_id).first()
                    role_menu_subs[user_role.role.name] = {'title': user_role.role.name,
                                                 'class': 'change_role',
                                                 'data': {'role_id': user_role.role.id, 'facility': facility.name}}

        if role_menu_subs:
            subs = {'title': 'Change Role',
                    'subs': role_menu_subs}
        else:
            subs = {}
        return subs

    def get_page_form_data(self, page_form_name, page_context, active=1):
        page_form = None
        if page_form_name:
            page_form = (self.session.query(models.PageForm).
                filter(models.PageForm.name == page_form_name).first())
        if not page_form:
            return None, None, None

        if page_form.parent_id is None:
            page_form_ids = [page_form.id]
        else:
            page_forms = self.page_form_ancestors(page_form.id)

            page_form_ids = []
            for pf in page_forms:
                page_form_ids.append(pf[0])
                if pf[1].id != page_form.id:
                    for attr, value in pf[1].__dict__.items():
                        if not attr.startswith('__') and not callable(value):
                            if getattr(page_form, attr) == "" and value != "":
                                setattr(page_form, attr, value)

        return page_form, page_form_ids

    def page_form_ancestors(self, page_form_id, active = 1):
        res = self.session.query(models.PageForm).filter_by(id=page_form_id). \
            filter_by(active=active).first()

        if res is None:
            # in theory this should not be reached...
            return [(None,None)]
        elif res.parent_id is None:
            # base case
            return [(res.id, res)]
        else:
            return [(res.id, res)] + self.page_form_ancestors(res.parent_id, active)

    def page_form_buttons(self, page_form_ids, page_context, table_object_id = None, active=1):
        page_form_buttons = {'top': [], 'bottom': []}
        filters = [
                models.PageFormButtonRole.role_id == self.role.id,
                models.PageFormButton.active == active,
                models.PageFormButtonRole.active == active,
                models.PageFormButtonContext.active == active,
                models.PageFormContext.active == active,
                models.PageFormButtonContext.page_form_id.in_(page_form_ids),
                models.PageFormContext.name.in_(page_context)
        ]

        if table_object_id is not None:
            filters += [or_(models.PageFormButtonContext.table_object_id == table_object_id,
                            models.PageFormButtonContext.table_object_id == None)]
        else:
            filters += [models.PageFormButtonContext.table_object_id == None]

        res = (self.session.query(models.PageFormButton, models.SelectListItem)
               .join(models.PageFormButtonRole,
                     models.PageFormButtonRole.page_form_button_id == models.PageFormButton.id)
               .join(models.PageFormButtonContext,
                     models.PageFormButtonContext.page_form_button_id == models.PageFormButton.id)
               .join(models.PageFormContext,
                     models.PageFormButtonContext.page_form_context_id == models.PageFormContext.id)
               .join(models.SelectListItem,
                     models.SelectListItem.id == models.PageFormButtonContext.button_location_id)
               .order_by(models.PageFormButtonContext.order, models.PageFormButtonRole.order,
                         models.PageFormButton.order, models.PageFormButton.name)
               .filter(*filters))

        # query = res.statement.compile(dialect=mysql.dialect())
        # logging.info('query')
        # logging.info(str(query))
        # logging.info(str(query.params))
        res = res.all()

        for row in res:
            page_form_buttons[row.SelectListItem.display_name].append(row.PageFormButton)

        return page_form_buttons

    def page_form_javascript(self, page_form_ids, active=1):
        res = self.session.query(models.PageFormJavascript).\
            filter(models.PageFormJavascript.page_form_id.in_(page_form_ids)). \
            filter_by(active=active).order_by(models.PageFormJavascript.order, models.PageFormJavascript.id).all()

        return res

    def has_access(self, auth_type, criteria, active=1):
        table_object = getattr(models, auth_type)
        table_object_role = getattr(models, auth_type + "Role")

        filters = [
            getattr(table_object_role, 'role_id') == self.role.id,
            getattr(table_object, 'active') == active
        ]

        for column, value in criteria.items():
            filters.append(getattr(table_object, column) == value)

        rec = (self.session.query(table_object).
               join(table_object_role).
               filter(*filters).first())

        return rec

    def get_menu_items(self, parent_id, active=1):
        items = (self.session.query(models.Menu, models.Route, models.MenuRole, models.Module)
                 .join(models.MenuRole, models.MenuRole.menu_id==models.Menu.id)
                 .outerjoin(models.Route, models.Menu.route_id==models.Route.id)
                 .outerjoin(models.Module, models.Route.module_id==models.Module.id)
            .filter(
                models.MenuRole.role_id == self.role.id,
                models.MenuRole.active == active,
                models.Menu.parent_id == parent_id,
                models.Menu.active == active
            ).order_by(models.MenuRole.order, models.MenuRole.display_name,
                       models.Menu.order, models.Menu.display_name).all())

        return items

    def change_role(self, role_id):
        """updates the user.current_role
        """
        # check that the logged in user has permission for that role
        if self.user is None:
            return False
        user_role = self.session.query(models.UserRole, models.Role). \
            join(models.Role). \
            filter(models.UserRole.role_id == role_id). \
            filter(models.UserRole.user_id == self.user.id).first()
        if user_role.UserRole:
            facility = self.session.query(models.Facility).filter_by(id=user_role.Role.facility_id).first()
            self.user.current_user_role_id = user_role.UserRole.id
            self.role = (self.session.query(models.Role).filter(models.Role.id == role_id).first())
            self.session.commit()
            # remove orgs from session because current_org_id is facility
            if self.facility.name != facility.name and 'org_id' in session:
                session.pop('org_id')
            # renew the facility and routes
            self.__init__()
            self.set_routes()

            return facility.name
        else:
            return False

    def change_user(self, user_id):
        """updates the user
        """
        # check that the logged in user a role in common with the user
        if self.user is None:
            return False

        user = self.session.query(models.UserRole, models.User). \
            join(models.User, models.UserRole.user_id == models.User.id). \
            filter(models.UserRole.role_id.in_(self.facilities[self.facility.name]['roles'])). \
            filter(models.User.id == user_id).first()
        return user

    def get_link_tables(self, table_object, levels=2, level=1, child_only=False, active=1):
        link_tables = []

        if table_object.extends_table_object_id:
            res = self.get_extension_children(table_object.id, active)
        else:
            res = self.get_children(table_object.id, active)

        if len(res) > 0:
            for row in res:
                table_meta_data = row.extension or row.TableObject

                link_tables.append({'parent': table_object.name,
                                    'level': level,
                                    'table_meta_data': table_meta_data,
                                    'extended_table': row.extension == table_meta_data,
                                    'link_data': row.TableObjectChildren,
                                    'link_type': 'child'})

                if level < levels:
                    link_tables = link_tables + self.get_link_tables(table_meta_data,levels, level + 1, True)

        if not child_only:
            res = self.session.query(models.TableObjectMany). \
                filter(or_(models.TableObjectMany.first_table_object_id==table_object.id,
                           models.TableObjectMany.second_table_object_id==table_object.id)).\
                filter_by(active=active). \
                order_by(models.TableObjectMany.order, models.TableObjectMany.id).all()

            if len(res) > 0:
                for row in res:
                    if row.first_table_object_id == table_object.id:
                        table_data = self.has_access('TableObject', {'id': row.second_table_object_id})
                    else:
                        table_data = self.has_access('TableObject', {'id': row.first_table_object_id})

                    if table_data:
                        link_tables.append({'parent': table_object.name,
                                            'level': level,
                                            'table_meta_data': table_data,
                                            'extended_table': None,
                                            'link_data': row.TableObjectMany,
                                            'link_type': 'many'})

        return link_tables

    def get_children(self, table_object_id, active = 1):
        extension = aliased(models.TableObject, name='extension')
        return self.session.query(models.TableObjectChildren, models.TableObject, models.TableObjectRole,
                                 extension). \
            join(models.TableObject, models.TableObjectChildren.child_table_object_id == models.TableObject.id). \
            join(models.TableObjectRole,
                 models.TableObjectChildren.child_table_object_id == models.TableObjectRole.table_object_id). \
            outerjoin(extension, and_(extension.extends_table_object_id == models.TableObject.id,
                                      extension.name == models.TableObject.name + '_' + self.facility.table_suffix)). \
            filter(models.TableObjectChildren.table_object_id==table_object_id). \
            filter(models.TableObjectChildren.active==active). \
            filter(models.TableObjectRole.role_id==self.role.id). \
            filter(models.TableObjectRole.active==active). \
            order_by(models.TableObjectChildren.order, models.TableObject.name).all()

    def get_extension_children(self, table_object_id, active = 1):
        extension = aliased(models.TableObject, name='extension')
        extended_table = aliased(models.TableObject, name='extended_table')
        ext = self.session.query(models.TableObjectChildren, models.TableObject, models.TableObjectRole,
                                 extension). \
            join(extended_table,
                 extended_table.extends_table_object_id == models.TableObjectChildren.table_object_id). \
            join(models.TableObject,  models.TableObjectChildren.child_table_object_id == models.TableObject.id). \
            join(models.TableObjectRole, models.TableObject.id == models.TableObjectRole.table_object_id). \
            outerjoin(extension, and_(extension.extends_table_object_id == models.TableObject.id,
                                      extension.name == models.TableObject.name + '_' + self.facility.table_suffix)). \
            filter(extended_table.id==table_object_id). \
            filter(models.TableObjectChildren.active==active). \
            filter(models.TableObjectRole.role_id==self.role.id). \
            filter(models.TableObjectRole.active==active). \
            filter(models.TableObject.name + '_' + self.facility.table_suffix == extension.name). \
            order_by(models.TableObjectChildren.order, models.TableObject.name)

        # query = ext.statement.compile(dialect=mysql.dialect())
        # logging.info('query')
        # logging.info(str(query))
        # logging.info(str(query.params))

        return ext.all()

    def check_facility_module(self, facility, module, table_name, active=1):
        rec = (self.session.query(models.TableObject).
               join(models.TableObjectRole, models.TableObject.id == models.TableObjectRole.table_object_id).
               join(models.Role, models.TableObjectRole.role_id == models.Role.id).
               join(models.Facility, models.Role.facility_id == models.Facility.id).
               join(models.ModuleFacility, models.Facility.id == models.ModuleFacility.facility_id).
               join(models.Module, models.ModuleFacility.module_id == models.Module.id).
               filter(models.TableObject.active == active).
               filter(models.TableObjectRole.active == active).
               filter(models.Role.active == active).
               filter(models.Module.active == active).
               filter(models.Facility.active == active).
               filter(models.ModuleFacility.active == active).
               filter(models.TableObject.name == table_name).
               filter(models.TableObjectRole.role_id == self.role.id).
               filter(models.Facility.id == self.role.facility_id).
               filter(models.Facility.name == facility).
               filter(models.Module.name == module).first())

        return rec is None

    def check_facility(self, facility, table_name, active=1):
        rec = (self.session.query(models.TableObject).
               join(models.TableObjectRole).
               join(models.Role).
               join(models.Facility).
               filter(models.TableObject.active == active).
               filter(models.TableObjectRole.active == active).
               filter(models.Role.active == active).
               filter(models.Facility.active == active).
               filter(models.Facility.id == self.role.facility_id).
               filter(models.Facility.name == facility).
               filter(models.TableObjectRole.role_id == self.role.id).
               filter(models.TableObject.name == table_name).first())

        return rec is None

    def check_url3(self, facility, module, active=1):
        rec = (self.session.query(models.Facility).
               join(models.Module).
               join(models.ModuleFacility).
               filter(models.Module.active == active).
               filter(models.Facility.active == active).
               filter(models.ModuleFacility.active == active).
               filter(models.Facility.id == self.role.facility_id).
               filter(models.Facility.name == facility).
               filter(models.Module.name == module).first())

        return rec is None

    def has_facility_access(self, facility):
        if self.role.role_facility.name == facility:
            return True
        return False

    def workflow(self, workflow_name, active = 1):
        res = None
        if workflow_name:
            res = (self.session.query(models.Workflow).
                    join(models.WorkflowRole).
                filter(models.Workflow.name == workflow_name).
                filter(models.Workflow.active == active).
                filter(models.WorkflowRole.role_id == self.role.id).first())
        return res

    def workflow_steps(self, workflow_id, active = 1):
        res = None
        if workflow_id:
            res = (self.session.query(models.Step,
                models.Route, models.Module, models.Field, models.TableObject).
                join(models.Route).
                join(models.RouteRole).
                join(models.Module).
                outerjoin(models.TableObject, models.Step.table_object_id ==
                    models.TableObject.id).
                outerjoin(models.Field, models.Step.dynamic_field ==
                    models.Field.id).
                filter(models.Step.workflow_id == workflow_id).
                filter(models.RouteRole.role_id == self.role.id).
                filter(models.Step.active == active).
                filter(models.Route.active == active).
                order_by(models.Step.order).all())
        return res

    def get_role_row(self, table_name, params):
        table_object = util.get_table(table_name)
        table_object_role = util.get_table(table_name + '_role')

        criteria = [
                table_object_role.role_id == self.role.id,
                table_object.id == table_object_role.table_object_id
        ]

        for key, value in params.items():
            criteria.append(getattr(table_object, key) == value)

        result = self.session.query(table_object, table_object_role).filter(*criteria).first()
        return result

    def get_role_home(self):
        table_object = util.get_table('role')
        criteria = [(table_object.id == self.role.id)]
        result = self.session.query(table_object).filter(*criteria).first()
        return getattr(result, 'default_home')
