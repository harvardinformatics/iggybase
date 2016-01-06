$( document ).ready( function () {
    $("#data_entry").click(function(){$.fn.openDataEntry();});
    $('.summary_table').DataTable();
} );


( function( $ ) {
    $.fn.openDataEntry = function () {
        var hidden_fields = $("#hidden_fields");
        var url = '';
        var script_root = hidden_fields.find('input[name=script_root]').val();
        if (script_root) {
            url += '/' + script_root
        }
        url += '/' + hidden_fields.find('input[name=mod]').val()
            + '/data_entry/' + hidden_fields.find('input[name=table]').val()
            + '/' + hidden_fields.find('input[name=row_name]').val()
        window.location = (url);
    }
} ) ( jQuery );

