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
    $( '#create_invoice' ).click( function(){ return $.fn.createInvoice(table);} );
} );

( function( $ ) {
    $.fn.createInvoice = function (table) {
        var hidden_fields = $("#hidden_fields");
        var url_prefix = $URL_ROOT + hidden_fields.find('input[name=facility]').val()
            + '/' + hidden_fields.find('input[name=mod]').val() + '/';
        var year_month_url = '/' + $('#year_select').val() + '/' + $('#month_select').val();
        $.ajax({
                // TODO: put facility in hidden fields and access dynamically
                url:url_prefix + 'generate_invoices' + year_month_url,
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                table: table,
                success: function(response) {
                    response = JSON.parse(response);
                    console.log(response);
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
        window.location = url_prefix + 'invoice_summary' + year_month_url;
    }
} ) ( jQuery );