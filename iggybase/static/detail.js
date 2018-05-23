$( document ).ready( function () {
    $("#data_entry").click(function(){$.fn.openDataEntry();});
    $('.summary_table').DataTable();
    $("#clone").click(function(){$.fn.clone();});
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

( function( $ ) {
    $.fn.clone = function () {
        var tbl = $("#detail_table tr");
        var detail = {}
        for (var i=0;i<tbl.length;i++) {
            var tds = $(tbl[i]).find('td');
            var key = 'data_entry_' + tds[0].innerText.toLowerCase().replace(' ', '_') + '_1';
            detail[key] = tds[1].innerText;
        }
        console.log(detail);
        var detail_json = JSON.stringify(detail);
        console.log(detail_json);
        var hidden_fields = $("#hidden_fields");
        var url = $URL_ROOT;
        url += hidden_fields.find('input[name=facility]').val()
            + '/' + hidden_fields.find('input[name=mod]').val()
            + '/data_entry/' + hidden_fields.find('input[name=table]').val()
            + '/new?data=' + detail_json;
        window.location = (url);

    }
} ) ( jQuery );
