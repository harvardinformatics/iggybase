from flask.ext.login import current_user
from iggybase.database import db_session
from iggybase.mod_admin.models import Field, FieldGroupRole, TableObject, TableObjectGroupRole, Group, GroupRole
from config import get_config
import logging

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__ ( self ):
        conf = get_config( )
        #logging.debug( conf.LAB )

        group = db_session.query( Group ).filter_by( name = conf.GROUP ).first( )

        self.grouproles = db_session.query( GroupRole ).filter_by( group_id = group.id ).all( )

    def module_table_objects( self, module, active = 1 ):
        table_objects = [ ]

        #logging.debug( 'module_table_objects' )
        #logging.info ( 'module: ' + module )
        #logging.info ( 'active: ' + str( active ) )
        res = db_session.query( TableObject ).filter_by( module = module ).filter_by( active = active ).all( )
        for row in res:
            #logging.info ( 'table_object_id: ' + str( row.id ) + ' name: ' + row.name )
            for group_role in self.grouproles:
                #logging.info ( 'group_role.id: ' + str( group_role.id ) )
                access = db_session.query( TableObjectGroupRole ).filter_by( table_object_id = row.id ).filter_by( group_role_id = group_role.id ).filter_by( active = active ).first( )
                if access is not None:
                    table_objects.append( row )
                    break

        return table_objects

    def module_fields( self, table_object_id, active = 1 ):
        fields = [ ]

        #logging.debug( 'module_fields' )
        #logging.info ( 'table_object_id: ' + str( table_object_id ) )
        #logging.info ( 'active: ' + str( active ) )
        res = db_session.query( Field ).filter_by( table_object_id = table_object_id, active = active ).all( )
        for row in res:
            #logging.info ( 'field_id: ' + str( row.id ) )
            for group_role in self.grouproles:
                access = db_session.query( FieldGroupRole ).filter_by( field_id = row.id, group_role_id = group_role.id, active = active ).first( )
                if access is not None:
                    fields.append( row )
                    break

        return fields
