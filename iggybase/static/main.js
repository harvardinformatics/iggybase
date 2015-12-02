$( document ).ready( function () {
    $( ".lookupfield" ).each(
        function() {
            var spancls = "ui-icon ui-icon-search search-button"
            var spanstl = "display: inline-block;float:right;"
            $('<span class="'+spancls+'" style="'+spanstl+'" luid="'+$(this).attr('id')+'"/>').appendTo($(this).parent());
        }
    );
    $( ".search-button" ).click(
        function( ) {
            $.fn.searchPopUp( $( this ) );
        }
    );
} );

( function( $ ) {
    $.fn.searchPopUp = function ( ele ) {
        var luid = ele.attr( 'luid' );

        if ( luid.match( /^Child_.*/ ) )
            luid = luid.substr( 6 );

        if ($("#message_div").length > 0)
            $("#message_div").text("");

        var formurl = rootdir + "/html/" + searchtype + ".php?propid=" + propertyid + "&objtype=" + objtype + "&proptype="+proptype+"&renderer="+renderer+"&decorate=half";

        var formstr = $.fn.get_url(formurl);

        var tmpform = "<div>"+formstr+"</div>";

        $(tmpform).appendTo("#searchpage");

        $("#searchpage").dialog({
          autoOpen: false,
          modal:    true,
          width:    800,

          buttons: [
              {
                text:  "Cancel",
                click: function() { $(this).dialog("close"); }
              },
              {
                text: btnlabel,
                click: function() { $.fn.searchResults( searchtype, propertyid, proptype, objtype, pid, renderer, '' ); }
              }
          ]
        } );
    }
} ) ( jQuery );
