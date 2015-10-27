from iggybase.mod_admin.models import DataType
import sqlalchemy
from sqlalchemy.orm import relationship
from iggybase.mod_auth.facility_access_control import FacilityAccessControl
from iggybase.database import admin_db_session, Base
from types import new_class
import datetime
import logging, sys, inspect

class TableFactory:
    def __init__( self, module, active = 1 ):
        self.facility_access_control = FacilityAccessControl( )
        self.active = active

    def table_object_factory( self, class_name, table_object ):
        classattr = { "__tablename__": table_object.name }

        table_object_cols = self.facility_access_control.module_fields( table_object.id, self.active )

        for col in table_object_cols:
            #logging.info( col.field_name )
            classattr[ col.field_name ] = self.create_column( col )

        newclass = new_class( class_name, ( Base, ), { }, lambda ns: ns.update( classattr ) )

        return newclass

    def to_camel_case( self, snake_str ):
        components = snake_str.split('_')

        return "".join( x.title( ) for x in components )

    def create_column( self, attributes ):
        datatype = admin_db_session.query( DataType ).filter_by( id = attributes.data_type_id, active = 1 ).first( )

        #logging.info( datatype.name )

        dtclassname = getattr( sqlalchemy, datatype.name )

        if attributes.data_type_id == 2:
            dtinst = dtclassname( attributes.length )
        else:
            dtinst = dtclassname( )

        arg = { }

        if attributes.primary_key == 1:
            arg[ 'primary_key' ] = True

        if attributes.unique == 1:
            arg[ 'unique' ] = True

        if attributes.default != "":
            arg[ 'default' ] = attributes.default

        return sqlalchemy.Column( dtinst, **arg )

    def create_foreign_key( self, attributes ):
        datatype = admin_db_session.query( DataType ).filter_by( id = attributes.data_type_id, active = 1 ).first( )

        # logging.info( datatype.name )

        dtclassname = getattr( sqlalchemy, datatype.name )

        if attributes.data_type_id == 2:
            dtinst = dtclassname( attributes.length )
        else:
            dtinst = dtclassname( )

        arg = { }

        if attributes.primary_key == 1:
            arg[ 'primary_key' ] = True

        if attributes.unique == 1:
            arg[ 'unique' ] = True

        if attributes.default != "":
            arg[ 'default' ] = attributes.default

        return sqlalchemy.Column( dtinst, **arg )