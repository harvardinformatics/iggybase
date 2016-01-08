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
            $.fn.searchClick( $( this ) );
        }
    );
} );

( function( $ ) {

    $.fn.showModalDialog = function ( url, callbacktext, callback ) {
        $.ajax( {
            url: url,
            success: function ( resp ) {
                tmpform = "<div id='modal_dialog_content' class='modal-content'>"+resp
                tmpform += "<div class='modal-footer'>"

                if ( callback ) {
                    tmpform += "<button id='"+callbacktext+"' type='button' class='btn btn-default'>"+callbacktext+"</button>"
                }

                tmpform += "<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>"

                tmpform += "</div>";
                tmpform += "</div>";

                $(tmpform).appendTo("#modal_dialog");

                if ( callback ) {
                    $( '.modal-footer #' + callbacktext ).click( callback )
                }

                $("#dialog").modal( "show" );
            }
        } );
    }

    $.fn.searchClick = function ( ele ) {
        var field_name = ele.attr( 'luid' );
        var matches = field_name.match( /(\S+)_(\d+)/);
        var property_name = matches[ 1 ];
        var input_id = ele.attr( 'id' );
        var table_object = $( '#table_object_0' ).val( );

        if ($("#modal_dialog").length > 0)
            $("#modal_dialog").text("");

        var formurl = $SCRIPT_ROOT + "/core/search?table_object=" + table_object + "&property_name=" + property_name + "&field_name=" + field_name + "&input_id=" + input_id;

        $.fn.showModalDialog( formurl, "Search", $.fn.searchResults )
    }

    $.fn.searchResults = function ( ) {
        $("#dialog").modal( "hide" );

        $("#modal_dialog").text("");

        alert('hello');
    }
} ) ( jQuery );
