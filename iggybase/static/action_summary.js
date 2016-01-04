$(document).ready(function(){
    var table = $('.summary_table').DataTable({
        deferRender:true,
        scrollX:true,
        ajax:{
            'url':'ajax',
            'data': function(d) { d.search = window.location.search;}
        },
        dom:'Bfrtip',
        buttons:[
            'selectAll',
            'selectNone'
        ],
        select: {
            style:'multi'
        }
    });
    $("#edit").click(function(){$.fn.editSelected(table);});
} );

( function( $ ) {
    $.fn.editSelected = function (table) {
        var names = $.map(table.rows('.selected').data(), function (i) { return $(i[1]).text() });
        if (names.length > 0) {
            var hidden_fields = $("#hidden_fields");
            var url = '';
            var script_root = hidden_fields.find('input[name=script_root]').val();
            if (script_root) {
                url += '/' + script_root
            }
            url += '/' + hidden_fields.find('input[name=mod]').val()
                + '/multiple_entry/' + hidden_fields.find('input[name=table]').val()
                + '?row_names=' + JSON.stringify(names)
            window.location = (url);
        } else {
            alert("No rows selected.  Select rows to edit by clicking.");
        }
    }
} ) ( jQuery );
