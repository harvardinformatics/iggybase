$(document).ready(function(){
    var ajax_url = '';
    if(typeof $AJAX_ROUTE !== 'undefined') {
        ajax_url = $AJAX_ROUTE + 'ajax';
    } else {
        ajax_url = 'ajax';
    }
    var table = $('.summary_table').DataTable({
        deferRender:true,
        order:[],
        autoWidth:false,
        scrollX:true,
        ajax:{
            'url':ajax_url,
            'data': function(d) { d.search = window.location.search;}
        },
        dom:"<'row'<'col-md-6'B><'col-md-6'f>><'row'<'col-md-12't>><'row'<'col-md-12'i>><'row'<'col-md-6'l><'col-md-6'p>>",
        lengthMenu:[[10,25,50,100,-1],[10,25,50,100,'All']],
        buttons:[
            'selectAll',
            'selectNone',
            'csv'
        ],
        select: {
            style:'multi'
        }
    });
    $( '#edit' ).click( function(){ return $.fn.editSelected(table);} );
    $("#update_table").click(function(){$.fn.updateTable(table);});
    $("#choose_action").click(function(){$.fn.chooseAction(table);});
    $.fn.updateButtonText();
} );

( function( $ ) {
    $.fn.editSelected = function (table) {
        var hidden_fields = $("#hidden_fields");
        var table_name = hidden_fields.find('input[name=table]').val();
        var column_name = table_name + '|name';
        var names = $.map(table.rows('.selected').data(), function (i) { return $(i[column_name]).text()});
        if (names.length > 0) {
            var url = $URL_ROOT;
            url += hidden_fields.find('input[name=facility]').val()
                + '/' + hidden_fields.find('input[name=mod]').val()
                + '/multiple_entry/' + table_name
                + '/' + JSON.stringify(names);
            if ( url.length > 2000 )
                alert("You are overly ambitious, please select fewer items.");
            else
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
            var facility = hidden_fields.find('input[name=facility]').val();
            var column_defaults = hidden_fields.find('input[name=column_defaults]').val();
            var table_name = hidden_fields.find('input[name=table]').val();
            var message_fields = hidden_fields.find('input[name=message_fields]').val();
            $.fn.updateTableAjax(table, facility, table_name, column_defaults, ids, message_fields);
        } else {
            alert("No rows selected.  Select rows to edit by clicking.");
        }
    }
    $.fn.updateTableAjax = function (table, facility, table_name, updates, ids, message_fields) {
        $.ajax({
            url:$URL_ROOT + facility + '/core/update_table_rows/' + table_name,
            data: JSON.stringify({
                'updates': JSON.parse(updates),
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
                    message = 'Successfully Updated:<br>' + response.updated.join(',');
                    this.table.ajax.reload();
                } else {
                    message = 'Unable to update any rows.';
                }
                $('#page_message p').html(message);
            }
        });
    }
    $.fn.chooseAction = function (table) {
        var ids = $.map(table.rows('.selected').data(), function (i) {return i['DT_RowId']});
        if (ids.length > 0) {
            var action = $("#choose_action_options").val();
            var hidden_fields = $("#hidden_fields");
            var column_defaults = hidden_fields.find('input[name=column_defaults]').val();
            var table_name = hidden_fields.find('input[name=table]').val();
            var facility = hidden_fields.find('input[name=facility]').val();
            var message_fields = hidden_fields.find('input[name=message_fields]').val();
            $.fn.updateTableAjax(table, facility, table_name, action, ids, message_fields);
        } else {
            alert("No rows selected.  Select rows to edit by clicking.");
        }
    }
} ) ( jQuery );
