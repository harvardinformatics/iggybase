from iggybase.mod_admin.models import Type, TypeLabRole, Field, FieldLabRole, LabRole, Lab, DataType
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from iggybase.mod_auth.lab_authenticator import LabAuthenticator
from iggybase.database import admin_db_session, Base
import datetime
import logging

class ModelFactory:
    def __init__ ( self, module ):
        self.module = module
        self.authenticator = LabAuthenticator( )

    def createmodel ( self, active = 1 ):
        types = self.authenticator.module_types( self.module, active )

        for modeltype in types:
            typeprops = self.authenticator.module_fields( modeltype.id, active )

            props = [ row.fieldname for row in typeprops ]

            classname = self.to_camel_case( modeltype.name )

            tableclass = self.createtype( classname, modeltype.name, props, Base )

            for propname in props:
                attributes = self.authenticator.fields( modeltype.id, active )
                coldef = self.columndefinition( attributes )
                setattr( tableclass, propname, coldef )

    def createtype ( self, name, tablename, argnames, baseclass ):
        def __init__( self, **kwargs ):
            for key, value in kwargs.items( ):
                if key not in argnames:
                    raise TypeError( "Argument %s not valid for %s" % ( key, self.__class__.__name__ ) )
                setattr( self, key, value )
            baseclass.__init__( self, name[ :-len( "Class" ) ] )
        newclass = type( name, ( baseclass, ), { "__init__": __init__, "__tablename__": tablename } )

        return newclass

    def to_camel_case( self, snake_str ):
        components = snake_str.split('_')

        return "".join( x.title( ) for x in components )

    def createcolumn( self, attributes ):
        datatype = admin_db_session.query( DataType ).filter_by( id = attributes.data_type_id, active = 1 ).first( )

        if attributes.data_type_id == 2:
            dtinst = datatype( attributes.length )
        else:
            dtinst = datatype( )

        arg = { }

        if attributes.primary_key == 1:
            arg[ 'primary_key' ] = True

        if attributes.unique == 1:
            arg[ 'unique' ] = True

        if attributes.default != "":
            arg[ 'default' ] = attributes.default

        return Column( dtinst, arg )