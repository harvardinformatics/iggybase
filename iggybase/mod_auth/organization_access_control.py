from flask import g
from iggybase.database import db_session
from iggybase.mod_auth.models import load_user, UserRole, Organization
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl
from importlib import import_module
from iggybase.database import admin_db_session
from iggybase.mod_admin import models
from iggybase.tablefactory import TableFactory
import logging

# Controls access to the data db data based on organization
# all data db access should run through this class
class OrganizationAccessControl:
    def __init__ ( self, module ):
        self.org_ids = [ ]
        self.module = module

        if g.user is not None and not g.user.is_anonymous:
            self.user = load_user( g.user.id )
            self.user_role = db_session.query( UserRole ).filter_by( id = self.user.current_user_role_id ).first( )
            self.facility_role_access_control = FacilityRoleAccessControl( )

            self.get_child_organization( self.user_role.organization_id )
        else:
            self.user = None
            self.user_role = None

    def get_child_organization( self, parent_organization_id ):
        self.org_ids.append( parent_organization_id )

        child_orgs = db_session.query( Organization ).filter_by( parent_id = parent_organization_id ).all( )

        if child_orgs is None:
            return

        for child_org in child_orgs:
            self.get_child_organization( child_org.id )

        return

    def get_entry_data( self, table_name, name = None, query_data = None ):
        field_data = self.get_field_data( table_name )

        results = None

        if field_data is not None:
            module_model = import_module( 'iggybase.' + self.module + '.models' )
            table_object = getattr( module_model, table_name )

            columns = [ ]
            for row in  field_data:
                if row.FieldFacilityRole.visible == 1:
                    columns.append( getattr( table_object, row.Field.field_name ).\
                                label( row.FieldFacilityRole.display_name ) )

            if name is None:
                results = db_session.query( *columns ).\
                    filter( getattr( table_object, 'organization_id' ).in_( self.org_ids ) ).all( )
            else:
                results = db_session.query( *columns ).\
                    filter_by( name = name ).\
                    filter( getattr( table_object, 'organization_id' ).in_( self.org_ids ) ).all( )

        return results

    def get_summary_data( self, table_name, query_data = { } ):
        field_data = self.get_field_data( table_name )

        results = None
        fk_table_objects = [ ]

        if field_data is not None:
            module_model = import_module( 'iggybase.' + self.module + '.models' )
            table_object = getattr( module_model, table_name )

            columns = [ ]
            for row in  field_data:
                if row.FieldFacilityRole.visible == 1:
                    if row.Field.foreign_key_table_object_id is not None:
                        fk_table_data = admin_db_session.query( models.TableObject ).\
                            filter_by( id = row.Field.foreign_key_table_object_id ).first( )

                        fk_table_name = TableFactory.to_camel_case( fk_table_data.name )

                        foreign_key_data = self.foreign_key( row.Field.foreign_key_table_object_id )

                        module_model = import_module( 'iggybase.' + foreign_key_data[ 'module' ] + '.models' )
                        fk_table_object = getattr( module_model, fk_table_name )

                        fk_table_objects.append( fk_table_object )

                        columns.append( getattr( table_object, row.Field.field_name ).\
                                        label( 'fk|' + fk_table_name + '|id' ) )

                        columns.append( getattr( fk_table_object, foreign_key_data[ 'foreign_key' ] ).\
                                        label( 'fk|' + foreign_key_data[ 'url_prefix' ] + '|' + fk_table_name + '|' +\
                                               foreign_key_data[ 'foreign_key_alias' ] ) )
                    else:
                        columns.append( getattr( table_object, row.Field.field_name ).\
                                        label( row.FieldFacilityRole.display_name ) )

                criteria = [ getattr( table_object, 'organization_id' ).in_( self.org_ids ) ]
                if 'criteria' in query_data:
                    for col, value in query_data[ 'criteria' ].items( ):
                        criteria.append( getattr( table_object, col ) == value )

            if not columns:
                results = db_session.query( table_object ).add_columns( *columns ).filter( *criteria ).all( )
            else:
                results = db_session.query( table_object, *fk_table_objects ).outerjoin( *fk_table_objects ).\
                    filter( *criteria ).add_columns( *columns ).all( )

        return self.format_data(results, table_object, fk_table_objects)

    def format_data(self, results, table_object, fk_table_objects):
        """Formats data for summary or detail
        - transforms into dictionary
        - removes model objects sqlalchemy puts in
        - formats FK data and link
        - formats name link which goes to detail template
        """
        table_rows = []
        # format results as dictionary
        if results:
            keys = results[0].keys()
            # filter out any objects
            keys_to_skip = [table_object.__name__]
            for fk in fk_table_objects:
                keys_to_skip.append(fk.__name__)
            # create dictionary for each row and for fk data
            for row in results:
                row_dict = {}
                for i, col in enumerate(row):
                    if keys[i] not in keys_to_skip:
                        if 'fk|' in keys[i] and '|name' in keys[i]:
                            fk_metadata = keys[i].split('|')
                            if fk_metadata[2]:
                                table = fk_metadata[2]
                                row_dict[table] = {
                                        'text': col,
                                        # add link foreign key table summary
                                        'link': '/' + fk_metadata[1] \
                                            + '/summary/' + table
                                }
                        else: # add all other colums to table_rows
                            row_dict[keys[i]] = {'text': col}
                            # name column values will link to detail
                            if keys[i] == 'name':
                                row_dict[keys[i]]['link'] = '/murray/detail/' \
                                    + table_object.__name__ + '/' + str(col)
                table_rows.append(row_dict)
        return table_rows

    def get_template_data( self, table_name, name ):
        query_data = { 'criteria': { 'name': name } }
        return self.get_summary_data( table_name, query_data )

    def foreign_key( self, table_object_id ):
        res = admin_db_session.query( models.Field, models.FieldFacilityRole, models.Module ).\
            join( models.FieldFacilityRole ).\
            join( models.Module ).\
            filter( models.Field.table_object_id == table_object_id ).\
            filter( models.Field.field_name == 'name' ).\
            order_by( models.FieldFacilityRole.order, models.FieldFacilityRole.id ).first( )

        ret_data = { }
        ret_data[ 'foreign_key' ] = res.Field.field_name
        ret_data[ 'foreign_key_alias' ] = res.FieldFacilityRole.display_name
        ret_data[ 'module' ] = res.Module.name
        ret_data[ 'url_prefix' ] = res.Module.url_prefix

        return ret_data

    def get_field_data( self, table_name ):
        table_data = self.facility_role_access_control.has_access( 'TableObject', table_name )

        field_data = None

        if table_data is not None:
            field_data = self.facility_role_access_control.fields( table_data.id, self.module )

        return field_data
