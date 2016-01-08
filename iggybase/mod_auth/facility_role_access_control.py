from collections import OrderedDict as OrderedDict
from flask import g, request
from sqlalchemy.orm import aliased
from iggybase.database import admin_db_session
from iggybase.mod_admin import models
from iggybase.mod_admin import constants as admin_consts
from iggybase.mod_auth.models import load_user
from config import get_config
import logging


# Controls access to system based on Role (USER) and Facility (config)
# Uses the permissions stored in the admin db
class FacilityRoleAccessControl:
    def __init__(self):
        config = get_config()
        self.facility = admin_db_session.query(models.Facility).filter_by(name=config.FACILITY).first()

        # set user and facility_role
        if g.user is not None and not g.user.is_anonymous:
            self.user = load_user(g.user.id)
            self.facility_role = (admin_db_session.query(models.FacilityRole).
                filter_by(facility_id=self.facility.id, role_id=self.user.current_user_role_id).first())
        else:
            self.user = None
            self.facility_role = None

    def fields(self, table_object_id, module, field_name = None, active=1):
        module = admin_db_session.query(models.Module, models.ModuleFacilityRole).join(models.ModuleFacilityRole). \
            filter(models.ModuleFacilityRole.facility_role_id == self.facility_role.id). \
            filter(models.Module.name == module).first()

        if module is None:
            return []

        filters = [
            (models.FieldFacilityRole.facility_role_id ==
                self.facility_role.id),
            (models.Field.table_object_id == table_object_id),
            (models.Field.active == active),
            (models.FieldFacilityRole.active == active),
            (models.FieldFacilityRole.module_id == module.Module.id)
        ]
        if field_name:
            filters.append((models.Field.field_name == field_name))
        res = admin_db_session.query(models.Field, models.FieldFacilityRole).join(models.FieldFacilityRole). \
            filter(*filters). \
            order_by(models.FieldFacilityRole.order, models.FieldFacilityRole.id).all()

        if res is None:
            return []
        else:
            return res

    def table_queries(self, page_form, table_name=None, active=1):
        """Get the table queries
        """
        filters = [
            (models.PageForm.name == page_form),
            (models.PageFormFacilityRole.facility_role_id ==
             self.facility_role.id),
            (models.TableQuery.active == active)
        ]
        if table_name:
            filters.append(
                (models.TableObject.name == table_name)
            )

        table_queries = (
            admin_db_session.query(
                models.TableQueryRender,
                models.TableQuery
            ).
                join(models.PageFormFacilityRole).
                join(models.PageForm).
                join(models.TableQuery).
                join(models.TableQueryTableObject).
                join(
                models.TableObject,
                models.TableQueryRender.table_object_id == models.TableObject.id
            ).
                filter(*filters).all()
        )
        return table_queries

    def table_query_fields( self, table_query_id, table_name = None, table_id = None, field_name = None, active = 1, visible = 1 ):
        filters = [

                (models.FieldFacilityRole.facility_role_id == self.facility_role.id),
                (models.TableObjectFacilityRole.facility_role_id == self.facility_role.id),
                (models.FieldFacilityRole.visible == visible),
                (models.Field.active == active),
                (models.FieldFacilityRole.active == active),
                (models.TableObject.active == active)
        ]

        # add filter for the identifier
        if table_query_id:
            filters.append((models.TableQueryField.table_query_id == table_query_id))
            filters.append((models.TableQueryField.active == active))
        elif table_name:
            filters.append((models.TableObject.name == table_name))
        elif table_id:
            filters.append((models.TableObject.id == table_id))

        # add any field_name filter
        if field_name:
            filters.append((models.Field.field_name == field_name))

        res = (
            admin_db_session.query(
                models.Field,
                models.TableObject,
                models.TableQueryField,
                models.Module
            ).
            join(
                models.TableObject,
                models.TableObject.id == models.Field.table_object_id
            ).
            join(models.FieldFacilityRole).
            join(models.TableObjectFacilityRole).
            join(models.Module).
            outerjoin(models.TableQueryField).
            filter(*filters).all()
        )
        return res

    def table_query_criteria(self, table_query_id):
        criteria = (
            admin_db_session.query(
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
                models.TableObjectFacilityRole,
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
        navbar_root = admin_db_session.query(models.Menu). \
            filter_by(name=admin_consts.MENU_NAVBAR_ROOT).first()
        navbar = get_menu_items(navbar_root.id, self.facility_role.id, active)

        sidebar_root = admin_db_session.query(models.Menu). \
            filter_by(name=admin_consts.MENU_SIDEBAR_ROOT).first()
        sidebar = get_menu_items(sidebar_root.id, self.facility_role.id, active)

        return navbar, sidebar

    def page_forms(self, active=1):
        page_forms = []

        res = admin_db_session.query(models.PageFormFacilityRole). \
            filter_by(facility_role_id=self.facility_role.id).filter_by(active=active). \
            order_by(models.PageFormFacilityRole.order, models.PageFormFacilityRole.id).all()
        for row in res:
            page_form = admin_db_session.query(models.PageForm). \
                filter_by(id=row.page_form_id).filter_by(active=active).first()
            if page_form is not None:
                page_forms.append(page_form)
                break

        return page_forms

    def page_form_buttons(self, page_form_id, active=1):
        page_form_buttons = {}
        page_form_buttons['top'] = []
        page_form_buttons['bottom'] = []

        res = admin_db_session.query(models.PageFormButtonFacilityRole). \
            filter_by(facility_role_id=self.facility_role.id).filter_by(active=active). \
            order_by(models.PageFormButtonFacilityRole.order, models.PageFormButtonFacilityRole.id).all()
        for row in res:
            page_form_button = admin_db_session.query(models.PageFormButton).filter_by(id=row.page_form_button_id). \
                filter_by(page_form_id=page_form_id).filter_by(active=active).first()
            if page_form_button is not None and page_form_button.button_location in ['top', 'bottom']:
                page_form_buttons[page_form_button.button_location].append(page_form_button)
                break

        return page_form_buttons

    def page_form_javascript(self, page_form_id, active=1):
        res = admin_db_session.query(models.PageFormJavaScript).filter_by(page_form_id=page_form_id). \
            filter_by(active=active).order_by(models.PageFormJavaScript.order, models.PageFormJavaScript.id).all()

        return res

    def has_access(self, auth_type, criteria, active=1):
        table_object = getattr(models, auth_type)
        table_object_role = getattr(models, auth_type + "FacilityRole")

        filters = [
            getattr(table_object_role, 'facility_role_id') == self.facility_role.id,
            getattr(table_object, 'active') == active
        ]
        if criteria['name']:
            filters.append(getattr(table_object, 'name') == criteria['name'])
        elif criteria['id']:
            filters.append(getattr(table_object, 'id') == criteria['id'])

        rec = (admin_db_session.query(table_object).
            join(table_object_role).
            filter(*filters).first())

        return rec

def get_menu_items(parent_id, facility_role_id, active=True):
    """Recursively Get menus items and subitems
    """
    menu = OrderedDict()
    items = (admin_db_session.query(models.Menu, models.MenuUrl)
        .join(models.MenuFacilityRole)
        .outerjoin(models.MenuUrl)
        .filter(
            models.MenuFacilityRole.facility_role_id == facility_role_id,
            models.Menu.parent_id == parent_id,
            models.Menu.active == active
        )
        .order_by(models.Menu.order, models.Menu.name).all())
    for item in items:
        url = get_menu_url(item)
        menu[item.Menu.description] = {
                'url': url,
                'name': item.Menu.name,
                'subs': get_menu_items(item.Menu.id, facility_role_id, active)
        }
    return menu

def get_menu_url(item):
    url = ''
    if item.MenuUrl:
        url = item.MenuUrl.url_path
        if url and item.MenuUrl.url_params:
            url += item.MenuUrl.url_params
    if url:
        if request.script_root:
            url = '/' + request.script_root + url
    else:
        url = '#'
    return url
