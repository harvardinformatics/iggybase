from collections import OrderedDict as OrderedDict
from flask import g, request, session
from iggybase.database import db_session
from iggybase.admin import models
from iggybase.admin import constants as admin_consts
from sqlalchemy import or_
import logging


# Controls access to system based on oole (USER) and Facility
# Uses the permissions stored in the admin db
class RoleAccessControl:
    def __init__(self):
        self.session = db_session()
        # set user and role
        if g.user is not None and not g.user.is_anonymous:
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
                self.session.flush()
                self.session.commit()
                self.role = role_data.Role
            else:
                self.role = (self.session.query(models.Role)
                             .join(models.UserRole)
                             .filter(models.UserRole.id==self.user.current_user_role_id).first())

            # TODO check if current user role is set, if not set
            self.role = (self.session.query(models.Role)
                         .join(models.UserRole)
                         .filter(models.UserRole.id == self.user.current_user_role_id).first())
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
                    self.facilities[fac.Facility.name] = fac.Role.id
                if fac.Role.id == self.role.id:
                    self.facility = fac.Facility
                    self.level_id = fac.Role.level_id

            if 'routes' in session and session['routes']:
                self.routes = session['routes']
                self.set_routes()
            else:
                self.set_routes()
        else:
            self.user = None
            self.role = None
            self.routes = []
            self.level_id = None
            self.facility = None

    def __del__(self):
        self.session.commit()

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

        res = self.session.query(models.Field, models.FieldRole).join(models.FieldRole). \
            filter(*filters). \
            order_by(models.FieldRole.order, models.FieldRole.display_name).all()

        if res is None:
            return {'Field': {}, 'FieldRole': {}}
        else:
            return res

    def table_queries(self, page_form, table_name=None, active=1):
        """Get the table queries
        """
        filters = [
            (models.PageForm.name == page_form),
            (models.PageFormRole.role_id == self.role.id),
            (models.TableQuery.active == active)
        ]
        if table_name:
            filters.append(
                (models.TableObject.name == table_name)
            )

        table_queries = (
            self.session.query(
                models.TableQueryRender,
                models.TableQuery
            ).
                join(models.PageFormRole).
                join(models.PageForm).
                join(models.TableQuery).
                join(models.TableQueryTableObject).
                join(
                models.TableObject,
                models.TableQueryRender.table_object_id == models.TableObject.id
            ).
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
                               models.TableQueryField, models.Field).
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

    def table_query_fields(self, table_query_id, table_name=None, table_id=None, display_name=None, field_id=None,
                           active=1):
        filters = [
            (models.FieldRole.role_id == self.role.id),
            (models.TableObjectRole.role_id == self.role.id),
            (models.Field.active == active),
            (models.FieldRole.active == active),
            (models.TableObject.active == active)
        ]
        selects = [
            models.Field,
            models.TableObject,
            models.FieldRole,
            models.TableObjectRole
        ]
        joins = [
            models.FieldRole,
            models.TableObjectRole
        ]
        orders = [
            models.FieldRole.order,
            models.Field.order
        ]
        outerjoins = []

        # add filter for the identifier
        if table_query_id:
            filters.append((models.TableQueryField.table_query_id == table_query_id))
            filters.append((models.TableQueryField.active == active))
            selects.append(models.TableQueryField)
            selects.append(models.TableQueryCalculation)
            joins.append(models.TableQueryField)
            outerjoins.append(models.TableQueryCalculation)
            orders = [
                models.TableQueryField.order,
                models.Field.order
            ]
        elif table_name:
            filters.append((models.TableObject.name == table_name))
        elif table_id:
            filters.append((models.TableObject.id == table_id))

        # add any field_name filter
        if display_name:
            filters.append((models.Field.display_name == display_name))
        elif field_id:
            filters.append((models.Field.id == field_id))

        res = (
            self.session.query(*selects).
                join(
                models.TableObject,
                models.TableObject.id == models.Field.table_object_id
                ).
                join(*joins).
                outerjoin(*outerjoins).
                filter(*filters).order_by(*orders).all()
        )
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
        self.routes = []
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
        for row in res:
            path =  self.facility.name + '/' + row.Module.name + '/' + row.Route.url_path
            self.routes.append(path)
        session['routes'] = self.routes

    def route_access(self, route):
        route = route.strip('/')
        route = route.split('/')
        route = '/'.join(route[:3])
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

    def page_form_menus(self, page_form_id, active=True):
        """Setup NavBar and Side bar menus for templating context.
        Starts with the root navbar and sidebar records.
        Menus are recursive.
        """
        # TODO: do we need to query for this or can we just use constant
        navbar_root = self.session.query(models.Menu). \
            filter_by(name=admin_consts.MENU_NAVBAR_ROOT).first()
        navbar = self.get_menu_items(navbar_root.id, active)

        # add facility role change options to navbar
        navbar['Role'] = self.make_role_menu()

        sidebar_root = self.session.query(models.Menu). \
            filter_by(name=admin_consts.MENU_SIDEBAR_ROOT).first()
        sidebar = self.get_menu_items(sidebar_root.id, active)
        return navbar, sidebar

    def make_role_menu(self):
        role_menu_subs = OrderedDict({})
        if self.user is not None:
            for role in self.user.roles:
                if role.id != self.role.id:
                    facility = self.session.query(models.Facility).filter_by(id=role.facility_id).first()
                    role_menu_subs[role.name] = {'title': role.name,
                                                 'class': 'change_role',
                                                 'data': {'role_id': role.id, 'facility': facility.name}}

        if role_menu_subs:
            subs = {'title': 'Change Role',
                    'subs': role_menu_subs}
        else:
            subs = {}
        return subs

    def get_page_form_data(self, page_form_name, active=1):
        page_form = self.has_access("PageForm", {'name': page_form_name})

        if page_form is None:
            return None

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

        page_form_javascript = self.page_form_javascript(page_form_ids, active)
        page_form_buttons = self.page_form_buttons(page_form_ids, active)

        return page_form, page_form_buttons, page_form_javascript

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

    def page_form_buttons(self, page_form_ids, active=1):
        page_form_buttons = {'top': [], 'bottom': []}
        filters = [
                models.PageFormButton.page_form_id.in_(page_form_ids),
                models.PageFormButtonRole.role_id == self.role.id,
                models.PageFormButton.active == active,
                models.PageFormButtonRole.active == active,
        ]
        res = (self.session.query(models.PageFormButton)
                .join(models.PageFormButtonRole,
                    models.PageFormButtonRole.page_form_button_id ==
                    models.PageFormButton.id)
            .filter(*filters)
            .order_by(models.PageFormButton.order, models.PageFormButton.id).all())
        for row in res:
            if row.button_location in ['top', 'bottom']:
                page_form_buttons[row.button_location].append(row)
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
        menu = OrderedDict()
        items = (self.session.query(models.Menu, models.Route, models.MenuRole, models.Module)
                 .join(models.MenuRole, models.MenuRole.menu_id==models.Menu.id)
                 .outerjoin(models.Route, models.Menu.route_id==models.Route.id)
                 .outerjoin(models.Module, models.Route.module_id==models.Module.id)
            .filter(
                models.MenuRole.role_id == self.role.id,
                models.MenuRole.active == active,
                models.Menu.parent_id == parent_id,
                models.Menu.active == active
            ).order_by(models.MenuRole.order, models.MenuRole.display_name, models.Menu.display_name).all())

        for item in items:
            url = ''
            if item.Route and item.Route.url_path and item.Route.url_path != '':
                if self.facility.name != '':
                    url = self.facility.name + '/' + item.Module.name + '/' + item.Route.url_path
                else:
                    url = item.Module.name + '/' + item.Route.url_path
                if url and item.Menu.dynamic_suffix:
                    url += '/' + item.Menu.dynamic_suffix

                if url and item.Menu.url_params:
                    url += item.Menu.url_params

                if url:
                    url = request.url_root + url
                else:
                    url = '#'

            menu[item.Menu.name] = {
                    'url': url,
                    'title': item.Menu.display_name,
                    'class': None,
                    'subs': self.get_menu_items(item.Menu.id, active)
            }
        return menu

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
            # renew the facility and routes
            self.__init__()
            self.set_routes()
            return facility.name
        else:
            return False

    def get_link_tables(self, table_object_id, child_only=False, active=1):
        link_tables = {}
        link_data = {}

        res = self.session.query(models.TableObjectChildren). \
            filter_by(table_object_id=table_object_id).filter_by(active=active). \
            order_by(models.TableObjectChildren.order, models.TableObjectChildren.child_table_object_id).all()

        if len(res) > 0:
            child_tables = []
            child_data = []

            for row in res:
                table_data = self.has_access('TableObject', {'id': row.child_table_object_id})
                if table_data:
                    child_tables.append(table_data)
                    child_data.append(row)

            if len(child_tables) > 0:
                link_tables['child'] = child_tables
                link_data['child'] = child_data

        if not child_only:
            res = self.session.query(models.TableObjectMany). \
                filter(or_(models.TableObjectMany.first_table_object_id==table_object_id,
                           models.TableObjectMany.second_table_object_id==table_object_id)).\
                filter_by(active=active). \
                order_by(models.TableObjectMany.order, models.TableObjectMany.id).all()

            if len(res) > 0:
                many_tables = []
                many_data = []

                for row in res:
                    table_data = self.has_access('TableObject', {'id': row.child_table_object_id})
                    if table_data:
                        many_tables.append(table_data)
                        many_data.append(row)

                if len(many_tables) > 0:
                    link_tables['many'] = many_tables
                    link_data['many'] = many_data

        return link_data, link_tables

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
            res = (self.session.query(models.Step, models.TableObject,
                models.Route, models.Module, models.Field).
                join(models.TableObject).
                join(models.Route).
                join(models.RouteRole).
                join(models.Module).
                outerjoin(models.Field, models.Step.dynamic_field ==
                    models.Field.id).
                filter(models.Step.workflow_id == workflow_id).
                filter(models.RouteRole.role_id == self.role.id).
                filter(models.Step.active == active).
                filter(models.Route.active == active).
                order_by(models.Step.order).all())
        return res

