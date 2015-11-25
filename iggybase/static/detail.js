$( document ).ready( function () {
    $( "#data_entry" ).click( function( ) {
        var context = $(this).data('context');
        window.location = ('/' + context['mod'] + '/data_entry/' + context['table'] + '/' + context['row_name']);
    } );
} );


( function( $ ) {
    $.fn.openDataEntry = function () {
        //window.open( '/murray/data_entry/Address/test', '_self' );
    }
} ) ( jQuery );

