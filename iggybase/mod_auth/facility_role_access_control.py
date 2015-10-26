from flask.ext.login import current_user
from iggybase.database import admin_db_session
from iggybase.mod_admin.models import FacilityRole, Facility, TableObject, TableObjectFacilityRole,\
    Field, FieldFacilityRole, Action, ActionFacilityRole, Menu, MenuFacilityRole, MenuItem, MenuItemFacilityRole, \
    PageForm, PageFormFacilityRole, PageFormButtons, PageFormButtonsFacilityRole
from iggybase.mod_auth.models import load_user
from config import get_config

# Controls access to system based on Role (USER) and Facility (config)
# Uses the permissions stored in the admin db
class FacilityRoleAccessControl:
    def __init__ ( self ):
        config = get_config( )

        self.user = load_user( current_user.id )

        self.facility = admin_db_session.query( Facility ).filter_by( name = config.FACILITY ).first( )

        self.facilityrole = admin_db_session.query( FacilityRole ).filter_by( facility_id = self.facility.id, role_id = self.user.role_id ).first( )

    def table_objects( self, active = 1 ):
        table_objects = [ ]

        res = admin_db_session.query( TableObjectFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            table_object = admin_db_session.query( TableObject ).filter_by( id = row.table_object_id ).filter_by( active = active ).first( )
            if table_object is not None:
                table_objects.append( table_object )
                break

        return table_objects

    def fields( self, type_id, active = 1 ):
        fields = [ ]

        res = admin_db_session.query( FieldFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            field = admin_db_session.query( Field ).filter_by( id = row.field_id ).filter_by( active = active ).first( )
            if field is not None:
                fields.append( field )
                break

        return fields

    def actions( self, active = 1 ):
        actions = [ ]

        res = admin_db_session.query( ActionFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            action = admin_db_session.query( Action ).filter_by( id = row.action_id ).filter_by( active = active ).first( )
            if action is not None:
                actions.append( action )
                break

        return actions

    def menus( self, active = 1 ):
        menus = [ ]

        res = admin_db_session.query( MenuFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            menu = admin_db_session.query( Menu ).filter_by( id = row.menu_id ).filter_by( active = active ).first( )
            if menu is not None:
                menus.append( menu )
                break

        return menus

    def menu_items( self, menu_id, active = 1 ):
        menu_items = [ ]

        res = admin_db_session.query( MenuItemFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            menuitem = admin_db_session.query( MenuItem ).filter_by( id = row.menu_item_id ).filter_by( active = active ).first( )
            if menuitem is not None:
                menu_items.append( menuitem )
                break

        return menu_items

    def page_forms( self, active = 1 ):
        page_forms = [ ]

        res = admin_db_session.query( PageFormFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            page_form = admin_db_session.query( PageForm ).filter_by( id = row.page_form_id ).filter_by( active = active ).first( )
            if page_form is not None:
                page_forms.append( page_form )
                break

        return page_forms

    def page_form_buttons( self, menu_id, active = 1 ):
        page_form_buttons = [ ]

        res = admin_db_session.query( PageFormButtonsFacilityRole ).filter_by( facility_role_id = self.facilityrole.id ).filter_by( active = active ).all( )
        for row in res:
            page_form_button = admin_db_session.query( PageFormButtons ).filter_by( id = row.page_form_button_id ).filter_by( active = active ).first( )
            if page_form_button is not None:
                page_form_buttons.append( page_form_button )
                break

        return page_form_buttons

    #def has_access( self, auth_type, name, active = 1 ):
        #qry = SelectQuery( auth_type )
        #qry.criteria( [ 'name', '=', name ] )
        #auth_type_res = qry.execute( )

        #auth_type_id = auth_type_res[ 0 ][ 'id' ]
        #qry = SelectQuery( auth_type + "FacilityRole" )
        #qry.criteria( [ 'facility_role_id', '=', self.facilityrole.id ] )
        #qry.criteria( [ auth_type + '_id', '=', auth_type_id ] )
        #res = qry.execute( )

        #if res[ 0 ][ 'permission' ]:
        #    return res[ 0 ][ 'permission' ]
        #else:
        #    return None