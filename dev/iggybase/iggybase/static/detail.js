$( document ).ready( function () {
    $("#data_entry").click(function(){$.fn.openDataEntry();});
    $('.summary_table').DataTable();
} );


( function( $ ) {
    $.fn.openDataEntry = function () {
        var hidden_fields = $("#hidden_fields");
        var url = $URL_ROOT;
        url += hidden_fields.find('input[name=facility]').val()
            + '/' + hidden_fields.find('input[name=mod]').val()
            + '/data_entry/' + hidden_fields.find('input[name=table]').val()
            + '/' + hidden_fields.find('input[name=row_name]').val()
        window.location = (url);
    }
} ) ( jQuery );

