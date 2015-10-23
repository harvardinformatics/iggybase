from iggybase.mod_admin.models import DataType
import sqlalchemy
from sqlalchemy.orm import relationship
from iggybase.mod_auth.group_access_control import GroupAccessControl
from iggybase.database import admin_db_session, Base
import datetime
import logging

group_access_control = GroupAccessControl( )

def createmodel ( module, active = 1 ):
    table_objects = group_access_control.module_table_objects( module, active )

    for table_object in table_objects:

        #logging.info( 'table name: ' + to_camel_case( table_object.name ) )

        #colnames = [ row.field_name for row in table_object_cols ]

        class_name = to_camel_case( table_object.name )

        table_object_factory ( class_name, table_object, active )

    cont = Container()

def table_object_factory ( class_name, table_object, active = 1 ):
    def __init__( self, **kwargs ):
        Base.__init__( self, class_name )

    classattr = { "__init__": __init__, "__tablename__": table_object.name }

    table_object_cols = group_access_control.module_fields( table_object.id, active )

    for col in table_object_cols:
        #logging.info( col.field_name )
        classattr[ col.field_name ] = create_column( col )

    newclass = type( class_name, ( Base, ), classattr )

    test = newclass( )
    logging.info( 'new class: ' +  class_name )
    logging.info( test )

    return newclass

def to_camel_case( snake_str ):
    components = snake_str.split('_')

    return "".join( x.title( ) for x in components )

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