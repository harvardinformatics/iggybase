$( document ).ready( function () {
    $( "#login_register" ).click( function( ) { $.fn.openRegistration( ); } );
} );


( function( $ ) {
    $.fn.openRegistration = function ( ) {
        window.open( '/register', '_self' );
    }
} ) ( jQuery );