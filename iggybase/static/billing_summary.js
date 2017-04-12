$(document).ready(function(){
    var path = window.location.pathname;
    var last_path_part = path.split('/').slice(-2)[0];
    var ajax_url = 'ajax';
    if (last_path_part == 'review') { // add year and month
        ajax_url = $('#year').val() + '/' + $('#month').val() + '/ajax';
    }
    var table = $('.summary_table').DataTable({
        deferRender:true,
        scrollX:true,
        ajax:{
            'url': ajax_url
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
        },
        /*footerCallback: function(row, data, start, end, display) {
            var api = this.api();
            var intVal = function (i, def) {
                return typeof i == 'string' ? i.replace(/[\$,]/g, '')*1 :
                    typeof i == 'number' ? i : def;
            };
            var tot = [];
            var tot2 = [];
            api.data().each(function (v, k) {
              if ((k % 2) == 0) {
                tot[k] = intVal(v[11], 0) + intVal(v[12], 1);
              } else {
                tot2[k] = intVal(v[11], 0) + intVal(v[12], 1);
              }
            });
            var red1 = (tot.reduce(function (a, b) { return a + b;}, 0)
                        ).toFixed(2);
            var red2 = (tot2.reduce(function (a, b) { return a + b;}, 0)
                        ).toFixed(2);

            $(api.column(11).footer()).html("total: $" + red1 + " and " + red2
            );
        }*/

    });
    $( '#edit' ).click( function(){ return $.fn.editSelected(table);} );
    $( '#create_invoice, #regenerate' ).click( function(){ return $.fn.createInvoice(table);} );
    $('#year, #month').change(function() {
        var ajax_url = $('#year').val() + '/' + $('#month').val() + '/ajax';
        table.ajax.url(ajax_url).load();
    });
} );

( function( $ ) {
    $.fn.editSelected = function (table) {
        var hidden_fields = $("#hidden_fields");
        var table_name = hidden_fields.find('input[name=table]').val();
        var column_name = table_name + '|name';
        var names = $.map(table.rows('.selected').data(), function (i) { return $(i[0]).text()});
        if (names.length > 0) {
            var url = $URL_ROOT;
            url += hidden_fields.find('input[name=facility]').val()
                + '/core'
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
        var table_name = hidden_fields.find('input[name=table]').val();
        var column_name = table_name + '|';
        // this code runs on line_item and invoice tables
        if (table_name == 'invoice') {
            column_name += 'invoice_organization_id';
        } else {
            column_name += 'organization_id';
        }
        var test = table.rows('.selected').data();
        var orgs = $.map(table.rows('.selected').data(), function (i) { return $(i[column_name]).text()});
        var url_prefix = $URL_ROOT + hidden_fields.find('input[name=facility]').val()
            + '/' + hidden_fields.find('input[name=mod]').val() + '/';
        var year_month_url = '/' + $('#year').val() + '/' + $('#month').val() + '/';
        var message = '';
        $.ajax({
                url:url_prefix + 'generate_invoices' + year_month_url,
                data: JSON.stringify({'orgs': orgs}),
                contentType: 'application/json;charset=UTF-8',
                type: 'POST',
                table: table,
                success: function(response) {
                    response = JSON.parse(response);
                    if(response.generated.length > 0) {
                        // success message will be flask flashed
                        window.location = url_prefix + 'invoice_summary' + year_month_url;
                    } else {
                        message = 'Unable to regenerate any rows.';
                        $('#page_message p').html(message);
                    }
                }
        });
    }
} ) ( jQuery );
