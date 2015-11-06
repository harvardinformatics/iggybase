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
            .append( $( '<option>', { value: '', text: '' } ) )
        ;

        $( '#organization' )
            .children( )
            .remove( )
            .end( )
            .append( $( '<option>', { value: '', text: '' } ) )
        ;

        if ( user == "" )
            return false;

        var data = { }
        data[ 'user' ] = user;

        $.ajax({
            url: "/auth/getrole",
            data: JSON.stringify( data, null, '\t' ),
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function( response ) {
                response = JSON.parse( response );

                for ( var id in response.roles ) {
                    if ( id != 'none' ) {
                        $( '#role' ).append($( '<option>', {
                            value: id,
                            text: response.roles[ id ]
                        }));

                        if ( id == response.current[ 'role' ] ) {
                            $( '#role' ).val( id );
                            $.fn.updateorganizationselect( $( '#role' ) );
                        }
                    }
                }
            }
        });
        $( "body" ).css( "cursor", "default" );
    }

    $.fn.updateorganizationselect = function ( ele ) {
    
    }
} ) ( jQuery );