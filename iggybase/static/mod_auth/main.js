$( document ).ready( function () {
    $( "#login_register" ).click( function( ) { $.fn.openRegistration( ); } );
    $( "#regcompletelogin" ).click( function( ) { $.fn.openLogin( ); } );
} );


( function( $ ) {
    $.fn.openRegistration = function ( ) {
        window.open( '/register', '_self' );
    }

    $.fn.openLogin = function ( ) {
        window.open( '/login', '_self' );
    }
} ) ( jQuery );