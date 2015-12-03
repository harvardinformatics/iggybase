$(document).ready(function(){
    $('.summary_table').DataTable({
        "order":[],
        "aoColumnDefs":[
            {"bSortable": false, "aTargets":[0]}
        ]
    });
    $("#select_all").click(function(){$.fn.toggleSelect();});
} );

( function( $ ) {
    $.fn.toggleSelect = function () {
        $("input.action_checkbox").click();
    }
} ) ( jQuery );
