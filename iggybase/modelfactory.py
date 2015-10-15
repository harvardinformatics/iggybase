from iggybase.mod_admin.models import TableObject, TableObjectLabRole, Field, FieldLabRole, LabRole, Lab, DataType
import sqlalchemy
from sqlalchemy.orm import relationship
from iggybase.mod_auth.lab_access_control import LabAccessControl
from iggybase.database import admin_db_session, Base
import datetime
import logging

class ModelFactory:
    def __init__ ( self, module ):
        self.module = module
        self.lab_access_control = LabAccessControl( )

    def createmodel ( self, active = 1 ):
        table_objects = self.lab_access_control.module_table_objects( self.module, active )

        for table_object in table_objects:

            #logging.info( 'table name: ' + ModelFactory.to_camel_case( table_object.name ) )

            #colnames = [ row.field_name for row in table_object_cols ]

            class_name = ModelFactory.to_camel_case( table_object.name )

            self.table_object_factory ( class_name, table_object, active )

    def table_object_factory ( self, class_name, table_object, active = 1 ):
        def __init__( self, **kwargs ):
            Base.__init__( self, class_name )

        classattr = { "__init__": __init__, "__tablename__": table_object.name }

        table_object_cols = self.lab_access_control.module_fields( table_object.id, active )

        for col in table_object_cols:
            #logging.info( col.field_name )
            classattr[ col.field_name ] = ModelFactory.create_column( col )

        newclass = type( class_name, ( Base, ), classattr )

        return newclass

    @staticmethod
    def to_camel_case( snake_str ):
        components = snake_str.split('_')

        return "".join( x.title( ) for x in components )

    @staticmethod
    def create_column( attributes ):
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

    @staticmethod
    def create_foreign_key( attributes ):
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