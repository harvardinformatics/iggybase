from iggybase.database import admin_db_session
from iggybase.mod_admin.models import Field, FieldFacilityRole, TableObject, TableObjectFacilityRole, Facility, FacilityRole, Module, PageForm, PageFormButton, PageFormButtonFacilityRole, Action
from config import get_config
import logging

# Controls access to system based on Group (config)
# Uses the permissions stored in the admin db
# independent of requests, used to build the models for sqlalchemy
class FacilityAccessControl:
    def __init__ ( self ):
        conf = get_config( )
        #logging.debug( conf.FACILITY )

        facility = admin_db_session.query( Facility ).filter_by( name = conf.FACILITY ).first( )

        self.facilityroles = admin_db_session.query( FacilityRole ).filter_by( facility_id = facility.id ).all( )

    def facility_module_table_objects( self, module, active = 1 ):
        table_objects = [ ]

        module_rec = admin_db_session.query( Module ).filter_by( name = module ).first( )

        #logging.debug( 'module_table_objects' )
        #logging.info ( 'module: ' + module )
        #logging.info ( 'active: ' + str( active ) )
        res = admin_db_session.query( TableObject ).filter_by( active = active ).all( )
        for row in res:
            #logging.info ( 'table_object_id: ' + str( row.id ) + ' name: ' + row.name )
            for facility_role in self.facilityroles:
                #logging.info ( 'facility_role.id: ' + str( facility_role.id ) )
                access = admin_db_session.query( TableObjectFacilityRole ).filter_by( table_object_id = row.id ).filter_by( module_id = module_rec.id ).filter_by( facility_role_id = facility_role.id ).filter_by( active = active ).first( )
                if access is not None:
                    table_objects.append( row )
                    break

        return table_objects

    def facility_module_fields( self, table_object_id, active = 1 ):
        fields = [ ]

        #logging.debug( 'module_fields' )
        #logging.info ( 'table_object_id: ' + str( table_object_id ) )
        #logging.info ( 'active: ' + str( active ) )
        res = admin_db_session.query( Field ).filter_by( table_object_id = table_object_id, active = active ).all( )
        for row in res:
            #logging.info ( 'field_id: ' + str( row.id ) )
            for facility_role in self.facilityroles:
                access = admin_db_session.query( FieldFacilityRole ).filter_by( field_id = row.id, facility_role_id = facility_role.id, active = active ).first( )
                if access is not None:
                    fields.append( row )
                    break

        return fields

    def facility_buttons( self, page_form, active = 1 ):
        button_objects = [ ]

        page_form_rec = admin_db_session.query( PageForm ).filter_by( name = page_form ).first( )

        res = admin_db_session.query( PageFormButton ).filter_by( page_form_id = page_form_rec.id ).filter_by( active = active ).all( )
        for row in res:
            #logging.info ( 'table_object_id: ' + str( row.id ) + ' name: ' + row.name )
            for facility_role in self.facilityroles:
                #logging.info ( 'facility_role.id: ' + str( facility_role.id ) )
                access = admin_db_session.query( PageFormButtonFacilityRole ).filter_by( page_form_button_id = row.id ).filter_by( facility_role_id = facility_role.id ).filter_by( active = active ).first( )
                if access is not None:
                    button_objects.append( row )
                    break

        return button_objects
