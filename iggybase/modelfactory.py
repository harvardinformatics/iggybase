from iggybase.mod_admin.models import DataType
import sqlalchemy
from sqlalchemy.orm import relationship
from iggybase.mod_auth.facility_access_control import FacilityAccessControl
from iggybase.database import admin_db_session, Base
import datetime
import logging

facility_access_control = FacilityAccessControl( )

def table_object_factory( class_name, table_object, active = 1 ):
    classattr = { "__tablename__": table_object.name }

    table_object_cols = facility_access_control.module_fields( table_object.id, active )

    for col in table_object_cols:
        #logging.info( col.field_name )
        classattr[ col.field_name ] = create_column( col )

    newclass = type( class_name, ( Base, ), classattr )

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

# def file_header( modfile ):
#     modfile.seek( 0 )
#     modfile.truncate( )
#
#     modfile.write( 'from iggybase.database import Base, StaticBase\n' )
#     modfile.write( 'from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime\n' )
#     modfile.write( 'from sqlalchemy.orm import relationship\n' )
#     modfile.write( 'import datetime\n\n' )