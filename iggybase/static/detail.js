$( document ).ready( function () {
    $("#data_entry").click(function(){$.fn.openDataEntry();});
} );


( function( $ ) {
    $.fn.openDataEntry = function () {
        var hidden_fields = $("#hidden_fields");
        window.location = (
            '/' + hidden_fields.find('input[name=mod]').val()
            + '/data_entry/' + hidden_fields.find('input[name=table]').val()
            + '/' + hidden_fields.find('input[name=row_name]').val()
        );
    }
} ) ( jQuery );

