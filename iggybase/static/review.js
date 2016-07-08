$(document).ready(function(){
    var columns = [];
    $('th').each(function(){
        columns.push({data: $(this).data('name')});
    });
    var ajax_url = $('#year_select').val() + '/' + $('#month_select').val() + '/ajax';
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
    $( '#edit' ).click( function(){ return $.fn.editSelected(table);} );
    $( '#create_invoice' ).click( function(){ return $.fn.createInvoice(table);} );
    $('#year_select, #month_select').change(function() {
        var ajax_url = $('#year_select').val() + '/' + $('#month_select').val() + '/ajax';
        table.ajax.url(ajax_url).load();
    });
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

    $.fn.createInvoice = function (table) {
        var hidden_fields = $("#hidden_fields");
        var url_prefix = $URL_ROOT + hidden_fields.find('input[name=facility]').val()
            + '/' + hidden_fields.find('input[name=mod]').val() + '/';
        var year_month_url = '/' + $('#year_select').val() + '/' + $('#month_select').val() + '/';
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
                    if(response.generated.length > 0) {
                        message = 'Successfully Generated:<br>' + response.generated.join(',');
                    } else {
                        message = 'Unable to update any rows.';
                    }
                    $('#page_message p').html(message);
                }
        });
        window.location = url_prefix + 'invoice_summary' + year_month_url;
    }
} ) ( jQuery );
