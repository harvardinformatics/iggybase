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
    $( ".datepicker-field" ).datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true

    });
    $( "form .lookupfield" ).keydown(function (e) {
        var key = e.which;
        if(key == 13)  // the enter key code
        {
            var input_id = $(this).attr( 'id' );
            var matches = input_id.match( /(\S+)_(\d+)/);
            var field_name = matches[ 1 ];
            var table_object = $( '#table_object_0' ).val( );
            var module = $( '#module_0' ).val( );
            var search_vals = {};

            search_vals['search_name'] = $(this).val();
            search_vals['modal_input_id'] = input_id;
            search_vals['modal_table_object'] = table_object;
            search_vals['modal_field_name'] = field_name;
            search_vals['modal_module'] = module;
            search_vals['modal_search_table'] = '';
            search_vals['modal_search_module'] = '';

            var formurl = $SCRIPT_ROOT + "/core/search_results?search_vals=" + JSON.stringify(search_vals);

            $("#modal_dialog").text("");

            $.fn.showModalDialog( formurl, {}, $.fn.searchLinks );

            return false;
        }
    });
} );

( function( $ ) {

    $.fn.showModalDialog = function ( url, buttons, callback ) {
        $.ajax( {
            url: url,
            success: function ( resp ) {
                tmpform = "<div id='modal_dialog_content' class='modal-content'>"+resp;
                tmpform += "<div class='modal-footer'>";

                if ( buttons ) {
                    for (var key in buttons){
                        tmpform += "<button id='"+key+"' type='button' class='btn btn-default'>"+key+"</button>";
                    }
                }

                tmpform += "<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>";

                tmpform += "</div>";
                tmpform += "</div>";

                $(tmpform).appendTo("#modal_dialog");

                if ( buttons ) {
                    for (var key in buttons){
                        $( '.modal-footer #' + key ).click( buttons[key] );
                    }
                }

                if ( callback )
                    $('#dialog').on('shown.bs.modal', function(e){ callback(); } );

                $("#dialog").modal( "show" );
            }
        } );
    }

    $.fn.searchClick = function ( ele ) {
        var input_id = ele.attr( 'luid' );
        var matches = input_id.match( /(\S+)_(\d+)/);
        var field_name = matches[ 1 ];
        var table_object = $( '#table_object_0' ).val( );
        var module = $( '#module_0' ).val( );

        if ($("#modal_dialog").length > 0)
            $("#modal_dialog").text("");

        var formurl = $SCRIPT_ROOT + "/core/search?table_object=" + table_object + "&input_id=" + input_id + "&field_name=" + field_name + "&module=" + module;

        var buttons = {};
        buttons[ "Search" ] = $.fn.searchResults;

        $.fn.showModalDialog( formurl, buttons );
    }

    $.fn.searchResults = function ( ) {
        $("#dialog").modal( "hide" );
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
        search_vals = {};

        $(".modal-body input").each(function() {
            search_vals[$(this).attr('id')] = $(this).val();
        });


        var formurl = $SCRIPT_ROOT + "/core/search_results?search_vals=" + JSON.stringify(search_vals);

        $("#modal_dialog").text("");

        $.fn.showModalDialog( formurl, {}, $.fn.searchLinks );
    }

    $.fn.searchLinks = function () {
        $(".search-results").click( function( ){ $.fn.searchUpdate( $(this) ); } );
    }

    $.fn.searchUpdate = function (ele) {
        $("#dialog").modal( "hide" );
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
        $("#" + ele.attr('luid')).val(ele.val());
    }
} ) ( jQuery );
