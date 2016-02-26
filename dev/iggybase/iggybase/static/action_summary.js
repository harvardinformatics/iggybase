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
            url += hidden_fields.find('input[name=facility]').val()
                + '/' + hidden_fields.find('input[name=mod]').val()
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
        var ids = $.map(table.rows('.selected').data(), function (i) {return i['DT_RowId']});
        if (ids.length > 0) {
            var hidden_fields = $("#hidden_fields");
            var column_defaults = hidden_fields.find('input[name=column_defaults]').val();
            var table_name = hidden_fields.find('input[name=table]').val();
            var message_fields = hidden_fields.find('input[name=message_fields]').val();
            $.ajax({
                // TODO: put facility in hidden fields and access dynamically
                url:$URL_ROOT + 'murray/core/ajax/update_table_rows/' + table_name,
                data: JSON.stringify({
                    'updates': JSON.parse(column_defaults),
                    'ids': ids,
                    'message_fields': JSON.parse(message_fields)
                }),
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                table: table,
                success: function(response) {
                    response = JSON.parse(response);
                    var message = '';
                    if(response.updated.length > 0) {
                        message = 'Successfully Updated:<br>' + response.updated.join('<br>');
                        this.table.ajax.reload();
                    } else {
                        message = 'Unable to update any rows.';
                    }
                    $('#page_message p').html(message);
                }
            });
        } else {
            alert("No rows selected.  Select rows to edit by clicking.");
        }
    }
} ) ( jQuery );
