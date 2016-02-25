$( document ).ready( function () {
    $( "#login_register" ).click( function( ) { $.fn.openRegistration( ); } );
    $( "#regcompletelogin" ).click( function( ) { $.fn.openLogin( ); } );
} );


( function( $ ) {
    $.fn.openRegistration = function ( ) {
        window.open( '/auth/register', '_self' );
    }

    $.fn.openLogin = function ( ) {
        window.open( '/auth/login', '_self' );
    }
} ) ( jQuery );