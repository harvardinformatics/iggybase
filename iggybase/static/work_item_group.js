$(document).ready(function(){
    if ($('.summary_table').length){
        var table = $('.summary_table').DataTable();
        $( '#wig_data' ).submit(function(e){ return $.fn.beforeNextStep(e, table);} );
    }
} );

( function( $ ) {
    $.fn.beforeNextStep = function (e, table) {
        var rows = $.map(table.rows('.selected').data(), function (i) { return {'table': 'line_item', 'id': i['DT_RowId'], 'column': 'name', 'name': $(i['name']).text()}});
        // TODO: make the tabletype dynamic
        var saved_rows = {'line_item': rows};
        $('#saved_rows').val(JSON.stringify(saved_rows));
    }
} ) ( jQuery );
