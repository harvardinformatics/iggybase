from flask import current_user
from iggybase.query import SelectQuery
from iggybase.mod_admin.models import LabRole, Lab
from iggybase.mod_auth.models import load_user
from config import get_config

class AccessControl:
    def __init__ ( self ):
        config = get_config( )

        self.user = load_user( current_user.id )

        qry = SelectQuery( [ 'Lab' ] )
        qry.criteria( [ 'name', '=', config.LAB ] )
        res = qry.execute( )

        self.lab = res[ 0 ]

        qry = SelectQuery( [ 'LabRole' ] )
        qry.criteria( [ 'lab_id', '=', self.lab.id ] )
        qry.criteria( [ 'role_id', '=',  self.user.role_id ] )
        res = qry.execute( )

        self.labrole = res[ 0 ]

    def types( self, active = 1 ):
        qry = SelectQuery( 'TypeLabRole' )
        qry.criteria( [ 'lab_role_id', '=', self.labrole.id ] )
        res = qry.execute( )

        types = [ ]

        for row in res:
            qry = SelectQuery( 'Type' )
            qry.criteria( [ 'id', '=', row [ 'type_id' ] ] )
            qry.criteria( [ 'active', '=', active ] )
            type_res = qry.execute( )
            types.append( type_res[ 0 ] )

        return types

    def fields( self, type_id, active = 1 ):
        qry = SelectQuery( 'FieldLabRole' )
        qry.criteria( [ 'lab_role_id', '=', self.labrole.id ] )
        res = qry.execute( )

        fields = [ ]

        for row in res:
            qry = SelectQuery( 'Field' )
            qry.criteria( [ 'id', '=', row [ 'field_id' ] ] )
            qry.criteria( [ 'active', '=', active ] )
            field_res = qry.execute( )
            fields.append( field_res[ 0 ] )

        return fields

    def actions( self, active = 1 ):
        qry = SelectQuery( 'ActionLabRole' )
        qry.criteria( [ 'lab_role_id', '=', self.labrole.id ] )
        res = qry.execute( )

        actions = [ ]

        for row in res:
            qry = SelectQuery( 'Action' )
            qry.criteria( [ 'id', '=', row [ 'action_id' ] ] )
            qry.criteria( [ 'active', '=', active ] )
            action_res = qry.execute( )
            actions.append( action_res[ 0 ] )

        return actions

    def menus( self, active = 1 ):
        qry = SelectQuery( 'MenuLabRole' )
        qry.criteria( [ 'lab_role_id', '=', self.labrole.id ] )
        res = qry.execute( )

        menus = [ ]

        for row in res:
            qry = SelectQuery( 'Menu' )
            qry.criteria( [ 'id', '=', row [ 'menu_id' ] ] )
            qry.criteria( [ 'active', '=', active ] )
            menu_res = qry.execute( )
            menus.append( menu_res[ 0 ] )

        return menus

    def menu_items( self, menu_id, active = 1 ):
        qry = SelectQuery( 'MenuItemLabRole' )
        qry.criteria( [ 'lab_role_id', '=', self.labrole.id ] )
        res = qry.execute( )

        menuitems = [ ]

        for row in res:
            qry = SelectQuery( 'MenuItem' )
            qry.criteria( [ 'id', '=', row [ 'menu_item_id' ] ] )
            qry.criteria( [ 'active', '=', active ] )
            field_res = qry.execute( )
            menuitems.append( field_res[ 0 ] )

        return menuitems

    def is_authorized( self, auth_type, name, active = 1 ):
        qry = SelectQuery( auth_type )
        qry.criteria( [ 'name', '=', name ] )
        auth_type_res = qry.execute( )

        auth_type_id = auth_type_res[ 0 ][ 'id' ]
        qry = SelectQuery( auth_type + "LabRole" )
        qry.criteria( [ 'lab_role_id', '=', self.labrole.id ] )
        qry.criteria( [ auth_type + '_id', '=', auth_type_id ] )
        res = qry.execute( )

        if res[ 0 ][ 'permission' ]:
            return res[ 0 ][ 'permission' ]
        else:
            return None