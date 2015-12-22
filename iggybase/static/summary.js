$(document).ready(function(){
    $('.summary_table').DataTable({
        'deferRender':true,
        'ajax':'ajax'
    });
    $('.datepicker').datepicker();

    // add event listeners for date range filter
    $('#min_date').keyup(function() {table.draw();});
    $('#max_date').keyup(function() {table.draw();});
    $("#download").click(function(){$.fn.openDownload();});
} );

( function( $ ) {
    $.fn.openDownload = function () {
        window.location = (location.pathname + '/download');
    }
} ) ( jQuery );
