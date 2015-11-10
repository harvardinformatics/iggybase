from flask.ext.login import current_user
from iggybase.database import admin_db_session
from iggybase.mod_admin import models
from iggybase.mod_auth.models import load_user
from config import get_config

# Controls access to system based on Role (USER) and Facility (config)
# Uses the permissions stored in the admin db
class FacilityRoleAccessControl:
    def __init__ ( self ):
        config = get_config( )

        self.facility = admin_db_session.query( models.Facility ).filter_by( name = config.FACILITY ).first( )

        if current_user.is_authenticated( ):
            self.user = load_user( current_user.id )
            self.facilityrole = admin_db_session.query( models.FacilityRole ).filter_by( facility_id = self.facility.id, role_id = self.user.role_id ).first( )
        else:
            self.user = None
            self.facilityrole = None

    def table_objects( self, active = 1 ):
        table_objects = [ ]

        res = admin_db_session.query( models.TableObjectFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            table_object = admin_db_session.query( models.TableObject ).filter_by( id = row.table_object_id ).filter_by( active = active ).first( )
            if table_object is not None:
                table_objects.append( table_object )
                break

        return table_objects

    def fields( self, type_id, active = 1 ):
        fields = [ ]

        res = admin_db_session.query( models.FieldFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            field = admin_db_session.query( models.Field ).filter_by( id = row.field_id ).filter_by( active = active ).first( )
            if field is not None:
                fields.append( field )
                break

        return fields

    def menus( self, active = 1 ):
        menus = [ ]

        res = admin_db_session.query( models.MenuFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            menu = admin_db_session.query( models.Menu ).filter_by( id = row.menu_id ).filter_by( active = active ).first( )
            if menu is not None:
                menus.append( menu )
                break

        return menus

    def menu_items( self, menu_id, active = 1 ):
        menu_items = [ ]

        res = admin_db_session.query( models.MenuItemFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            menuitem = admin_db_session.query( models.MenuItem ).filter_by( id = row.menu_item_id ). \
                filter_by( menu_id = menu_id ).filter_by( active = active ).first( )
            if menuitem is not None:
                menu_items.append( menuitem )
                break

        return menu_items

    def page_forms( self, active = 1 ):
        page_forms = [ ]

        res = admin_db_session.query( models.PageFormFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            page_form = admin_db_session.query( models.PageForm ).filter_by( id = row.page_form_id ).filter_by( active = active ).first( )
            if page_form is not None:
                page_forms.append( page_form )
                break

        return page_forms

    def page_form_buttons( self, page_form_id, active = 1 ):
        page_form_buttons = { }
        page_form_buttons[ 'top' ] = [ ]
        page_form_buttons[ 'bottom' ] = [ ]

        res = admin_db_session.query( models.PageFormButtonFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            page_form_button = admin_db_session.query( models.PageFormButton ).filter_by( id = row.page_form_button_id ). \
                filter_by( page_form_id = page_form_id ).filter_by( active = active ).first( )
            if page_form_button is not None and page_form_button.button_location in [ 'top', 'bottom' ]:
                page_form_buttons.append( page_form_button )
                break

        return page_form_buttons

    def page_form_javascript( self, page_form_id, active = 1 ):
        res = admin_db_session.query( models.PageFormJavaScript ).filter_by( page_form_id = page_form_id ).filter_by( active = active ).all( )

        return res

    def has_access( self, auth_type, name, active = 1 ):
        table_object = getattr( models, auth_type )
        table_col_id = table_object( ).__tablename__ + "_id"
        table_object_role = getattr( models, auth_type + "FacilityRole" )

        rec = admin_db_session.query( table_object ).filter_by( name = name ).first( )

        access = admin_db_session.query( table_object_role ).filter( getattr( table_object_role, table_col_id ) == rec.id ) \
            .filter_by( facility_role_id = self.facility_role.id ).filter_by( active = active ).first( )

        if access is not None:
            return rec

        return None
