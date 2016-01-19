from iggybase.database import db_session
from iggybase.mod_admin import models
from config import get_config
import logging

# Controls access to system based on Group (config)
# Uses the permissions stored in the admin db
# independent of requests, used to build the models for sqlalchemy
class FacilityAccessControl:
    def __init__ ( self ):
        conf = get_config( )
        #logging.debug( conf.FACILITY )

        facility = db_session.query( models.Facility ).filter_by( name = conf.FACILITY ).first( )

        self.facilityroles = db_session.query( models.FacilityRole ).filter_by( facility_id = facility.id ).all( )

    def module_table_objects( self, module, active = 1 ):
        table_objects = [ ]

        module_rec = db_session.query( models.Module ).filter_by( name = module ).first( )

        #logging.debug( 'module_table_objects' )
        #logging.info ( 'module: ' + module )
        #logging.info ( 'active: ' + str( active ) )
        res = db_session.query( models.TableObject ).filter_by( active = active ).\
            order_by( models.TableObject.order ).all( )
        for row in res:
            #logging.info ( 'table_object_id: ' + str( row.id ) + ' name: ' + row.name )
            for facility_role in self.facilityroles:
                #logging.info ( 'facility_role.id: ' + str( facility_role.id ) )
                access = db_session.query( models.TableObjectFacilityRole ).filter_by( table_object_id = row.id ).\
                    filter_by( module_id = module_rec.id ).filter_by( facility_role_id = facility_role.id ).\
                    filter_by( active = active ).first( )
                if access is not None:
                    table_objects.append( row )
                    break

        return table_objects

    def module_fields( self, table_object_id, active = 1 ):
        fields = [ ]

        #logging.debug( 'module_fields' )
        #logging.info ( 'table_object_id: ' + str( table_object_id ) )
        #logging.info ( 'active: ' + str( active ) )
        res = db_session.query( models.Field ).\
            filter_by( table_object_id = table_object_id, active = active ).all( )
        for row in res:
            #logging.info ( 'field_id: ' + str( row.id ) )
            for facility_role in self.facilityroles:
                access = db_session.query( models.FieldFacilityRole ).\
                    filter_by( field_id = row.id, facility_role_id = facility_role.id, active = active ).first( )
                if access is not None:
                    fields.append( row )
                    break

        return fields

    def page_form_buttons( self, page_form_id, active = 1 ):
        button_objects = { }
        button_objects[ 'top' ] = [ ]
        button_objects[ 'bottom' ] = [ ]

        res = db_session.query( models.PageFormButton ).\
            filter_by( page_form_id = page_form_id ).filter_by( active = active ).all( )
        for row in res:
            # logging.info ( 'table_object_id: ' + str( row.id ) + ' name: ' + row.name )
            for facility_role in self.facilityroles:
                # logging.info ( 'facility_role.id: ' + str( facility_role.id ) )
                access = db_session.query( models.PageFormButtonFacilityRole ).\
                    filter_by( page_form_button_id = row.id ) \
                    .filter_by( facility_role_id = facility_role.id ).filter_by( active = active ).first( )
                if access is not None and row.button_location in [ 'top', 'bottom' ]:
                    button_objects[ row.button_location ].append( row )
                    break

        return button_objects

    def page_form_javascript( self, page_form_id, active = 1 ):
        res = db_session.query( models.PageFormJavaScript ).filter_by( page_form_id = page_form_id ).\
            filter_by( active = active ).all( )

        return res

    def has_access( self, auth_type, name, active = 1 ):
        table_object = getattr( models, auth_type )
        table_col_id = table_object( ).__tablename__ + "_id"
        table_object_role = getattr( models, auth_type + "FacilityRole" )

        rec = db_session.query( table_object ).filter_by( name = name ).first( )

        for facility_role in self.facilityroles:
            # logging.info ( 'facility_role.id: ' + str( facility_role.id ) )

            access = db_session.query( table_object_role ).\
                filter( getattr( table_object_role, table_col_id ) == rec.id ).\
                filter_by( facility_role_id = facility_role.id ).filter_by( active = active ).first( )
            if access is not None:
                return rec

        return None

    def has_access_by_id( self, auth_type, id, active = 1 ):
        table_object = getattr( models, auth_type )
        table_col_id = table_object( ).__tablename__ + "_id"
        table_object_role = getattr( models, auth_type + "FacilityRole" )

        rec = db_session.query( table_object ).filter_by( id = id ).first( )

        for facility_role in self.facilityroles:
            # logging.info ( 'facility_role.id: ' + str( facility_role.id ) )

            access = db_session.query( table_object_role ).\
                filter( getattr( table_object_role, table_col_id ) == rec.id ).\
                filter_by( facility_role_id = facility_role.id ).filter_by( active = active ).first( )
            if access is not None:
                return rec

        return None
