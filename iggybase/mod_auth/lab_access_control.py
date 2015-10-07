from iggybase.query import SelectQuery
from config import get_config

class LabAccessControl:
    def __init__ ( self ):
        config = get_config( )

        qry = SelectQuery( [ 'Lab' ] )
        qry.criteria( [ 'name', '=', config.LAB ] )
        res = qry.execute( )

        self.lab = res[ 0 ]

        qry = SelectQuery( [ 'LabRole' ] )
        qry.criteria( [ 'lab_id', '=', self.lab.id ] )
        self.labroles = qry.execute( )

    def module_types( self, module, active = 1 ):
        types = [ ]
        type_id = { }

        for row1 in self.labroles:
            qry = SelectQuery( [ 'TypeLabRole' ] )
            qry.select( { 'type_id': 'type_id' } )
            qry.criteria( [ 'lab_role_id', '=', row1.id ] )
            qry.group_by( 'type_id' )
            res = qry.execute( )

            for row2 in res:
                type_id[ row2.id ] = row2.id

        for type in type_id:
            qry = SelectQuery( [ 'Type' ] )
            qry.criteria( [ 'id', '=', type ] )
            qry.criteria( [ 'active', '=', active ] )
            type_res = qry.execute( )
            try:
                types.append( type_res[ 0 ] )
            except ValueError:
                pass

        return types

    @staticmethod
    def module_fields( self, type_id, active = 1 ):
        fields = [ ]
        field_id = { }

        for row1 in self.labroles:
            qry = SelectQuery( [ 'FieldLabRole' ] )
            qry.select( { 'field_id': 'field_id' } )
            qry.criteria( [ 'lab_role_id', '=', row1.id ] )
            qry.group_by( 'field_id' )
            res = qry.execute( )

            for row2 in res:
                field_id[ row2.id ] = row2.id

        for field in field_id:
            qry = SelectQuery( [ 'Field' ] )
            qry.criteria( [ 'id', '=', field ] )
            qry.criteria( [ 'active', '=', active ] )
            field_res = qry.execute( )
            try:
                fields.append( field_res[ 0 ] )
            except ValueError:
                pass

        return fields
