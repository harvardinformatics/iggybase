from collections import OrderedDict as OrderedDict
from flask import g, request
from iggybase.database import db_session
from iggybase.mod_admin import models
from iggybase.mod_admin import constants as admin_consts
from config import get_config
import logging


# Controls access to system based on Role (USER) and Facility (config)
# Uses the permissions stored in the admin db
class RoleAccessControl:
    def __init__(self):
        config = get_config()
        # set user and role
        if g.user is not None and not g.user.is_anonymous:
            self.user = models.load_user(g.user.id)
            self.role = (db_session.query(models.Role)
                                  .join(models.UserRole)
                                  .filter(models.UserRole.id==self.user.current_user_role_id).first())
        else:
            self.user = None
            self.role = None

    def fields(self, table_object_id, filter=None, active=1):
        filters = [
            (models.FieldRole.role_id == self.role.id),
            (models.Field.table_object_id == table_object_id),
            (models.Field.active == active),
            (models.FieldRole.active == active)
        ]
        if filter is not None:
            for field_name, value in filter.items():
                field_data = field_name.split(".")
                if field_data[0] == "field":
                    filters.append((getattr(models.Field, field_data[1]) == value))
                else:
                    filters.append((getattr(models.FieldRole, field_data[1]) == value))

        res = db_session.query(models.Field, models.FieldRole).join(models.FieldRole). \
                    filter(*filters). \
                    order_by(models.FieldRole.order, models.FieldRole.id).all()

        if res is None:
            return []
        else:
            return res

    def table_queries(self, page_form, table_name=None, active=1):
        """Get the table queries
        """
        filters = [
            (models.PageForm.name == page_form),
            (models.PageFormRole.role_id ==
             self.role.id),
            (models.TableQuery.active == active)
        ]
        if table_name:
            filters.append(
                (models.TableObject.name == table_name)
            )

        table_queries = (
            db_session.query(
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

    def table_query_fields(self, table_query_id, table_name=None, table_id=None, field_name=None, active=1, visible=1):
        filters = [
            (models.FieldRole.role_id == self.role.id),
            (models.TableObjectRole.role_id == self.role.id),
            (models.FieldRole.visible == visible),
            (models.Field.active == active),
            (models.FieldRole.active == active),
            (models.TableObject.active == active)
        ]
        selects = [
            models.Field,
            models.TableObject,
            models.Module
        ]
        joins = [
            models.FieldRole,
            models.TableObjectRole,
            models.Module
        ]
        orders= [
            models.Field.order
        ]

        # add filter for the identifier
        if table_query_id:
            filters.append((models.TableQueryField.table_query_id == table_query_id))
            filters.append((models.TableQueryField.active == active))
            selects.append(models.TableQueryField)
            joins.append(models.TableQueryField)
            orders= [
                models.TableQueryField.order,
                models.Field.order
            ]
        elif table_name:
            filters.append((models.TableObject.name == table_name))
        elif table_id:
            filters.append((models.TableObject.id == table_id))

        # add any field_name filter
        if field_name:
            filters.append((models.Field.field_name == field_name))

        res = (
            db_session.query(*selects).
                join(
                models.TableObject,
                models.TableObject.id == models.Field.table_object_id
            ).
            join(*joins).
            filter(*filters).order_by(*orders).all()
        )
        return res

    def table_query_criteria(self, table_query_id):
        criteria = (
            db_session.query(
                models.TableQueryCriteria,
                models.Field,
                models.TableObject,
                models.Module
            ).join(
                models.Field
            ).join(
                (models.TableObject, models.Field.table_object_id ==
                 models.TableObject.id)
            ).join(
                models.TableObjectRole,
                models.Module
            ).
                filter(models.TableQueryCriteria.table_query_id == table_query_id).all()
        )
        return criteria

    def page_form_menus(self, page_form_id, active=True):
        """Setup NavBar and Side bar menus for templating context.
        Starts with the root navbar and sidebar records.
        Menus are recursive.
        """
        # TODO: do we need to query for this or can we just use constant
        navbar_root = db_session.query(models.Menu). \
            filter_by(name=admin_consts.MENU_NAVBAR_ROOT).first()
        navbar = self.get_menu_items(navbar_root.id, active)

        # add facility role change options to navbar
        navbar['Role'] = self.make_role_menu()

        sidebar_root = db_session.query(models.Menu). \
            filter_by(name=admin_consts.MENU_SIDEBAR_ROOT).first()
        sidebar = self.get_menu_items(sidebar_root.id, active)

        return navbar, sidebar

    def make_role_menu(self):
        role_menu_subs = {}
        for role in self.user.roles:
            role_menu_subs[role.name] = {'title':role.name,
                    'class':'change_role', 'data':{'role_id': role.id}}
        return {'title':'Change Role',
            'subs': role_menu_subs}

    def page_forms(self, active=1):
        page_forms = []

        res = db_session.query(models.PageFormRole). \
            filter_by(role_id=self.role.id).filter_by(active=active). \
            order_by(models.PageFormRole.order, models.PageFormRole.id).all()
        for row in res:
            page_form = db_session.query(models.PageForm). \
                filter_by(id=row.page_form_id).filter_by(active=active).first()
            if page_form is not None:
                page_forms.append(page_form)
                break

        return page_forms

    def page_form_buttons(self, page_form_id, active=1):
        page_form_buttons = {}
        page_form_buttons['top'] = []
        page_form_buttons['bottom'] = []

        res = db_session.query(models.PageFormButtonRole). \
            filter_by(role_id=self.role.id).filter_by(active=active). \
            order_by(models.PageFormButtonRole.order, models.PageFormButtonRole.id).all()
        for row in res:
            page_form_button = db_session.query(models.PageFormButton).filter_by(id=row.page_form_button_id). \
                filter_by(page_form_id=page_form_id).filter_by(active=active).first()
            if page_form_button is not None and page_form_button.button_location in ['top', 'bottom']:
                page_form_buttons[page_form_button.button_location].append(page_form_button)
                break

        return page_form_buttons

    def page_form_javascript(self, page_form_id, active=1):
        res = db_session.query(models.PageFormJavaScript).filter_by(page_form_id=page_form_id). \
            filter_by(active=active).order_by(models.PageFormJavaScript.order, models.PageFormJavaScript.id).all()

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

        rec = (db_session.query(table_object).
               join(table_object_role).
               filter(*filters).first())

        return rec

    def get_menu_items(self, parent_id, active=1):
        menu = OrderedDict()
        items = (db_session.query(models.Menu, models.MenuRole).join(models.MenuRole)
            .filter(
                models.MenuRole.role_id == self.role.id,
                models.Menu.parent_id == parent_id,
                models.MenuRole.active == active
            ).order_by(models.MenuRole.order, models.MenuRole.name).all())

        for item in items:
            url = ''
            if item.Menu.url_path and item.Menu.url_path != '':
                url = item.Menu.url_path
                if url and item.Menu.url_params:
                    url += item.Menu.url_params

                if url:
                    url = request.url_root + url
                else:
                    url = '#'

            menu[item.Menu.name] = {
                    'url': url,
                    'title': item.MenuRole.description,
                    'class': item.MenuRole.menu_class,
                    'subs': self.get_menu_items(item.Menu.id, active)
            }
        return menu

    def change_role(self, role_id):
        """updates the user.current_role
        """
        # check that the logged in user has permission for that role
        user = models.User.query.filter_by(id=self.user.id).first()
        user_role = models.UserRole.query.filter_by(role_id =
                role_id, user_id = user.id).first()
        if user_role:
            user.current_user_role_id = user_role.id
            db_session.commit()
            return True
        else:
            return False

    def get_child_tables(self, table_object_id, active = 1):
        child_tables = []
        link_data = []

        res = db_session.query(models.TableObjectChildren). \
            filter_by(table_object_id=table_object_id).filter_by(active=active). \
            order_by(models.TableObjectChildren.order, models.TableObjectChildren.child_table_object_id).all()

        for row in res:
            table_data = self.has_access('TableObject', {'id': row.child_table_object_id})
            if table_data:
                child_tables.append(table_data)
                link_data.append(row)

        return link_data, child_tables
