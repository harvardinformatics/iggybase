$(document).ready(function(){
    var columns = [];
    $('th').each(function(){
        columns.push({data: $(this).data('name')});
    });
    var ajax_url = 'ajax';
    var table = $('.summary_table').DataTable({
        deferRender:true,
        scrollX:true,
        ajax:{
            'url': ajax_url
        },
        columns: columns,
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
    $( '#regenerate' ).click( function(){ return $.fn.regenerate(table);} );
} );

( function( $ ) {
    $.fn.regenerate = function (table) {
        var hidden_fields = $("#hidden_fields");
        var table_name = hidden_fields.find('input[name=table]').val();
        var year = hidden_fields.find('input[name=year]').val();
        var month = hidden_fields.find('input[name=month]').val();
        var column_name = table_name + '|organization_id';
        var orgs = $.map(table.rows('.selected').data(), function (i) { return $(i[column_name]).text()});
        var url_prefix = $URL_ROOT + hidden_fields.find('input[name=facility]').val()
            + '/' + hidden_fields.find('input[name=mod]').val() + '/';
        $.ajax({
                // TODO: put facility in hidden fields and access dynamically
                url:url_prefix + 'generate_invoices/' + year + '/' + month + '/',
                data: JSON.stringify({
                    'orgs': orgs,
                }),
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                table: table,
                success: function(response) {
                    response = JSON.parse(response);
                    var message = '';
                    if(response.generated.length > 0) {
                        message = 'Successfully Generated:<br>' + response.generated.join(',');
                        this.table.ajax.reload();
                    } else {
                        message = 'Unable to regenerate any rows.';
                    }
                    $('#page_message p').html(message);
                }
        });
    }
} ) ( jQuery );
