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
            style:'single'
        }
    });
    $( '#continue' ).click( function(){ return $.fn.continueSelected(table);} );
    $("#new").click(function(){$.fn.openNew(table);});
} );

( function( $ ) {
    $.fn.continueSelected = function (table) {
        var row = table.rows('.selected').data();
        if (row.length > 0) {
            row = row[0];
            var hidden_fields = $("#hidden_fields");
            var url = window.location.href + row['work_item_group|step_id'] + '/' + $(row['work_item_group|name']).text();
            if ( url.length > 2000 )
                alert("You are overly ambitious, please select fewer items.");
            else
                window.location = (url);
        } else {
            alert("No rows selected.  Select rows to edit by clicking.");
        }
    }
    $.fn.openNew = function (table) {
        var hidden_fields = $("#hidden_fields");
        var workflow_name = hidden_fields.find('input[name=workflow_name]').val();
        var facility = hidden_fields.find('input[name=facility]').val();
        $.ajax({
            url:$URL_ROOT + facility + '/core/new_workflow/' + workflow_name + '/ajax',
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            table: table,
            success: function(response) {
                response = JSON.parse(response);
                var params = '';
                if (response.params) {
                    params = '?' + response.params;
                }
                var url = window.location.href + '1/' + response.work_item_group + params;
                window.location = (url);
            }
        });
    }
} ) ( jQuery );
