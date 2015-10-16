from flask import current_user
from iggybase.database import admin_db_session
from iggybase.mod_admin.models import LabRole, Lab, TableObject, TableObjectLabRole,\
    Field, FieldLabRole, Action, ActionLabRole, Menu, MenuLabRole, MenuItem, MenuItemLabRole, \
    PageForm, PageFormLabRole, PageFormButtons, PageFormButtonsLabRole
from iggybase.mod_auth.models import load_user
from config import get_config

class AccessControl:
    def __init__ ( self ):
        config = get_config( )

        self.user = load_user( current_user.id )

        self.lab = admin_db_session.query( Lab ).filter_by( name = conf.LAB ).first( )

        self.labrole = admin_db_session.query( LabRole ).filter_by( lab_id = lab.id, role_id = self.user.role_id ).first( )

    def table_objects( self, active = 1 ):
        table_objects = [ ]

        res = admin_db_session.query( TableObjectLabRole ).filter_by( lab_role_id = self.labrole.id ).filter_by( active = active ).all( )
        for row in res:
            table_object = admin_db_session.query( TableObject ).filter_by( id = row.table_object_id ).filter_by( active = active ).first( )
            if table_object is not None:
                table_objects.append( table_object )
                break

        return table_objects

    def fields( self, type_id, active = 1 ):
        fields = [ ]

        res = admin_db_session.query( FieldLabRole ).filter_by( lab_role_id = self.labrole.id ).filter_by( active = active ).all( )
        for row in res:
            field = admin_db_session.query( Field ).filter_by( id = row.field_id ).filter_by( active = active ).first( )
            if field is not None:
                fields.append( field )
                break

        return fields

    def actions( self, active = 1 ):
        actions = [ ]

        res = admin_db_session.query( ActionLabRole ).filter_by( lab_role_id = self.labrole.id ).filter_by( active = active ).all( )
        for row in res:
            action = admin_db_session.query( Action ).filter_by( id = row.action_id ).filter_by( active = active ).first( )
            if action is not None:
                actions.append( action )
                break

        return actions

    def menus( self, active = 1 ):
        menus = [ ]

        res = admin_db_session.query( MenuLabRole ).filter_by( lab_role_id = self.labrole.id ).filter_by( active = active ).all( )
        for row in res:
            menu = admin_db_session.query( Menu ).filter_by( id = row.menu_id ).filter_by( active = active ).first( )
            if menu is not None:
                menus.append( menu )
                break

        return menus

    def menu_items( self, menu_id, active = 1 ):
        menu_items = [ ]

        res = admin_db_session.query( MenuItemLabRole ).filter_by( lab_role_id = self.labrole.id ).filter_by( active = active ).all( )
        for row in res:
            menuitem = admin_db_session.query( MenuItem ).filter_by( id = row.menu_item_id ).filter_by( active = active ).first( )
            if menuitem is not None:
                menu_items.append( menuitem )
                break

        return menu_items

    def page_forms( self, active = 1 ):
        page_forms = [ ]

        res = admin_db_session.query( PageFormLabRole ).filter_by( lab_role_id = self.labrole.id ).filter_by( active = active ).all( )
        for row in res:
            page_form = admin_db_session.query( PageForm ).filter_by( id = row.page_form_id ).filter_by( active = active ).first( )
            if page_form is not None:
                page_forms.append( page_form )
                break

        return page_forms

    def page_form_buttons( self, menu_id, active = 1 ):
        page_form_buttons = [ ]

        res = admin_db_session.query( PageFormButtonsLabRole ).filter_by( lab_role_id = self.labrole.id ).filter_by( active = active ).all( )
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
        #qry = SelectQuery( auth_type + "LabRole" )
        #qry.criteria( [ 'lab_role_id', '=', self.labrole.id ] )
        #qry.criteria( [ auth_type + '_id', '=', auth_type_id ] )
        #res = qry.execute( )

        #if res[ 0 ][ 'permission' ]:
        #    return res[ 0 ][ 'permission' ]
        #else:
        #    return None