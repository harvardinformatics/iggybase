$(document).ready(function(){
    var table = $('.summary_table').DataTable({
        deferRender:true,
        scrollX:true,
        dom:"<'row'<'col-md-6'B><'col-md-6'f>><'row'<'col-md-12't>><'row'<'col-md-12'i>><'row'<'col-md-6'l><'col-md-6'p>>",
        buttons:[
            'csv'
        ],
        order: [],
        lengthMenu:[[10,25,50,100,-1],[10,25,50,100,'All']],
        ajax:{
            url:'ajax',
            data: function(d) { d.search = window.location.search;}
        }
    });
    $('.datepicker').datepicker();

    // add event listeners for date range filter
    $('#min_date, #max_date, #date_field_select').change(function() {table.draw();});
    $("#download").click(function(){$.fn.openDownload();});

    // add a date search to datatables
    $.fn.dataTable.ext.search.push(
        function(settings, data, dataIndex) {
            var min = Date.parse($('#min_date').val());
            var max = Date.parse($('#max_date').val());
            var created = Date.parse(data[$('#date_field_select').val()]);
            if ((isNaN(min) && isNaN(max)) ||
                    (isNaN(min) && created <= max) ||
                    (min <= created && isNaN(max)) ||
                    (min <= created && created <= max)) {
                return true;
            }
            return false;
        }
    );
} );

( function( $ ) {
    $.fn.openDownload = function () {
        window.location = (location.pathname + 'download');
    }
} ) ( jQuery );
