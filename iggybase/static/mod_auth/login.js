$( document ).ready( function () {
    $( "body" ).css( "cursor", "wait" );

    $( "#name" ).blur( function( ) { $.fn.updateroleselect( $( this ) ); } );

    $( "#role" ).change( function( ) { $.fn.updateorganizationselect( $( this ) ); } );

    $( "body" ).css( "cursor", "default" );
});

( function( $ ) {
    $.fn.updateroleselect = function ( ele ) {
        $( "body" ).css( "cursor", "wait" );
        var user = ele.val( );

        $( '#role' )
            .children( )
            .remove( )
            .end( )
        ;

        $( '#organization' )
            .children( )
            .remove( )
            .end( )
        ;

        if ( user == "" )
            return false;

        var data = { }
        data[ 'user' ] = user;

        $.ajax({
            url: $SCRIPT_ROOT + "/auth/getrole",
            data: JSON.stringify( data, null, '' ),
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function( response ) {
                response = JSON.parse( response );

                for ( var i in response.roles ) {
                    $( '#role' ).append($( '<option>', {
                        value: parseInt( response.roles[ i ][ 0 ] ),
                        text: response.roles[ i ][ 1 ]
                    }));

                    if ( response.roles[ i ][ 0 ] == response.current_role ) {
                        $( '#role' ).val( parseInt( response.roles[ i ][ 0 ] ) );
                        $.fn.updateorganizationselect( $( '#role' ) );
                    }
                }
                if ( response.orgs ) {
                    for ( var i in response.orgs ) {
                        $( '#organization' ).append($( '<option>', {
                            value: response.orgs[ i ][ 0 ],
                            text: response.orgs[ i ][ 1 ]
                        }));

                        if ( response.orgs[ i ][ 0 ] == response.current_organization )
                            $( '#organization' ).val( response.orgs[ i ][ 0 ] );
                    }
                }
            }
        });
        $( "body" ).css( "cursor", "default" );
    }

    $.fn.updateorganizationselect = function ( ele ) {
        $( "body" ).css( "cursor", "wait" );
        var role = ele.val( );

        $( '#organization' )
            .children( )
            .remove( )
            .end( )
        ;

        if ( role == "" )
            return false;

        var data = { }
        data[ 'user' ] = $( '#name' ).val( );
        data[ 'role' ] = role;

        $.ajax({
            url: $SCRIPT_ROOT + "/auth/getorganization",
            data: JSON.stringify( data, null, '' ),
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function( response ) {
                response = JSON.parse( response );

                for ( var i in response.orgs ) {
                    $( '#organization' ).append($( '<option>', {
                        value: response.orgs[ i ][ 0 ],
                        text: response.orgs[ i ][ 1 ]
                    }));

                    if ( response.orgs[ i ][ 0 ] == response.current_organization )
                        $( '#organization' ).val( response.orgs[ i ][ 0 ] );
                }
            }
        });
        $( "body" ).css( "cursor", "default" );
    }
} ) ( jQuery );