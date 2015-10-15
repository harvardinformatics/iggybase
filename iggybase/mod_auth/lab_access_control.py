from iggybase.database import admin_db_session
from iggybase.mod_admin.models import Field, FieldLabRole, TableObject, TableObjectLabRole, Lab, LabRole
from config import get_config
import logging

class LabAccessControl:
    def __init__ ( self ):
        conf = get_config( )
        #logging.debug( conf.LAB )

        lab = admin_db_session.query( Lab ).filter_by( name = conf.LAB ).first( )

        self.labroles = admin_db_session.query( LabRole ).filter_by( lab_id = lab.id ).all( )

    def module_table_objects( self, module, active = 1 ):
        table_objects = [ ]

        #logging.debug( 'module_table_objects' )
        #logging.info ( 'module: ' + module )
        #logging.info ( 'active: ' + str( active ) )
        res = admin_db_session.query( TableObject ).filter_by( module = module ).filter_by( active = active ).all( )
        for row in res:
            #logging.info ( 'table_object_id: ' + str( row.id ) + ' name: ' + row.name )
            for lab_role in self.labroles:
                #logging.info ( 'lab_role.id: ' + str( lab_role.id ) )
                access = admin_db_session.query( TableObjectLabRole ).filter_by( table_object_id = row.id ).filter_by( lab_role_id = lab_role.id ).filter_by( active = active ).first( )
                if access is not None:
                    table_objects.append( row )
                    break

        return table_objects

    def module_fields( self, table_object_id, active = 1 ):
        fields = [ ]

        #logging.debug( 'module_fields' )
        #logging.info ( 'table_object_id: ' + str( table_object_id ) )
        #logging.info ( 'active: ' + str( active ) )
        res = admin_db_session.query( Field ).filter_by( table_object_id = table_object_id, active = active ).all( )
        for row in res:
            #logging.info ( 'field_id: ' + str( row.id ) )
            for lab_role in self.labroles:
                access = admin_db_session.query( FieldLabRole ).filter_by( field_id = row.id, lab_role_id = lab_role.id, active = active ).first( )
                if access is not None:
                    fields.append( row )
                    break

        return fields
