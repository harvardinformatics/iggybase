$(document).ready(function(){
    $('.summary_table').DataTable({
        'deferRender':true,
        'scrollX':true,
        'ajax':{
            'url':'ajax',
            'data': function(d) { d.search = window.location.search;}
        }
    });
    $('.datepicker').datepicker();

    // add event listeners for date range filter
    $('#min_date, #max_date').change(function() {table.draw();});
    $("#download").click(function(){$.fn.openDownload();});

    // add a date search to datatables
    $.fn.dataTable.ext.search.push(
        function(settings, data, dataIndex) {
            var min = Date.parse($('#min_date').val());
            var max = Date.parse($('#max_date').val());
            var created = Date.parse(data[2]);
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
