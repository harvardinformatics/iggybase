from flask import g
from iggybase.database import admin_db_session, engine
from iggybase.mod_admin.models import Field, Type

class SelectQuery:
    def __init__( self, *types ):
        self.types = types
        self.select = { }
        self.criteria = [ ]
        self.order = { }
        self.group_by = [ ]

    def select( self, **select ):
        self.select.update( select )

    def criteria( self, *criteria ):
        self.criteria.append( criteria )

    def order( self, **order ):
        self.order.update( order )

    def group_by( self, *group_by ):
        self.group_by.append( group_by )

    def query( self ):
        qry = 'SELECT '
        qryprops = [ ]

        for tabletype in self.types:
            typedata = admin_db_session.query( Type ).filter_by( name = tabletype ).first( )
            typeprops = admin_db_session.query( Field ).filter_by( type_id = typedata.id ).all( )

            qryprops[ tabletype ] = [ ]
            for prop in typeprops:
                if self.select:
                    if prop in self.select:
                        qryprops[ tabletype ][ prop ] = "`" + tabletype + "." + prop + "`"
                        qry += tabletype + "." + prop + " as `" + tabletype + "." + prop + "`"
                        self.select.pop( prop )
                    elif tabletype + "." + prop in self.select:
                        qryprops[ tabletype ][ prop ] = "`" + tabletype + "." + prop + "`"
                        qry += tabletype + "." + prop + " as `" + tabletype + "." + prop + "`"
                        self.select.pop( tabletype + "." + prop )
                else:
                    qryprops[ tabletype ][ prop ] = "`" + tabletype + "." + prop + "`"
                    qry += tabletype + "." + prop + " as `" + tabletype + "." + prop + "`"

                if prop.foreign_key_type_id:
                    fkdata = admin_db_session.query( Type ).filter_by( id = prop.foreign_key_type_id ).first( )

                    if fkdata.name in self.types:
                        fkprops = admin_db_session.query( Field ).filter_by( type_id = prop.foreign_key_type_id, field_id = prop.foreign_key_field_id ).first( )

                        self.criteria.append( [ fkdata.name + "." + fkprops.name, "=", typedata.name + "." + prop.name ] )

        qry = qry[ :-2 ] + " FROM "

        for tabletype in self.types:
            qry += tabletype + ", "

        qry = qry[ :-2 ]

        if self.criteria is not None or len( self.types ) > 1:
            qry += " WHERE "

            for crit in self.criteria:
                qry += crit[ 0 ] + crit[ 1 ] + crit[ 2 ] + " AND "

            qry = qry[ :-4 ]

        if self.order is not None:
            qry += " ORDER BY "

            for ord in self.order:
                qry += ord[ 0 ] + " " + ord[ 1 ]

        return engine.execute( qry ).fetchall( )