$(document).ready(function(){
    $('.summary_table').DataTable();
    $("#download").click(function(){$.fn.openDownload();});
} );

( function( $ ) {
    $.fn.openDownload = function () {
        window.location = (location.pathname + '/download');
    }
} ) ( jQuery );
