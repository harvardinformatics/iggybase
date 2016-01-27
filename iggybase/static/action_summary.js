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
    $("#update_table").click(function(){$.fn.updateTable(table);});
    $.fn.updateButtonText();
} );

( function( $ ) {
    $.fn.editSelected = function (table) {
        var names = $.map(table.rows('.selected').data(), function (i) { return $(i[1]).text() });
        if (names.length > 0) {
            var hidden_fields = $("#hidden_fields");
            var url = $URL_ROOT;
            url += '/' + hidden_fields.find('input[name=mod]').val()
                + '/multiple_entry/' + hidden_fields.find('input[name=table]').val()
                + '?row_names=' + JSON.stringify(names)
            window.location = (url);
        } else {
            alert("No rows selected.  Select rows to edit by clicking.");
        }
    }
    $.fn.updateButtonText = function (table) {
        var hidden_fields = $("#hidden_fields");
        var button_text = hidden_fields.find('input[name=button_text]').val();
        $("#update_table").val(button_text);
    }
    $.fn.updateTable = function (table) {
        var ids = $.map(table.rows('.selected').data(), function (i) {return i[0]});
        if (ids.length > 0) {
            var hidden_fields = $("#hidden_fields");
            var column_defaults = hidden_fields.find('input[name=column_defaults]').val();
            var table = hidden_fields.find('input[name=table]').val();
            $.ajax({
                url:$URL_ROOT + 'ajax/update_table_rows/' + table,
                data: JSON.stringify({
                    'updates': JSON.parse(column_defaults),
                    'ids': ids
                }),
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                success: function(response) {
                    response = JSON.parse(response);
                    if(response.success) {
                        location.reload();
                    } else {
                        alert('rows could not be updated');
                    }
                }
            });
        } else {
            alert("No rows selected.  Select rows to edit by clicking.");
        }
    }
} ) ( jQuery );
