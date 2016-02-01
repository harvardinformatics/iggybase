$( document ).ready( function () {
    $( ".lookupfield" ).each(
        function( ) {
            $.fn.addLookup( $( this ) );
        }
    );
    $( ".search-button" ).click(
        function( ) {
            $.fn.searchClick( $( this ) );
        }
    );
    $( ".add_new_child_item" ).click(
        function( ) {
            $.fn.addChildTableRow( $( this ) );
        }
    );
    $( ".datepicker-field" ).datepicker(
        {
            format: 'yyyy-mm-dd',
            autoclose: true

        }
    );
    $( "form .lookupfield" ).keydown(
        function ( e ) {
            return $.fn.keydownLookupField( e, $( this ) );
        }
    );
    $( ".boolean-field" ).each(
        function( ) {
            $.fn.changeCheckBox( $( this) );
        }
    );
    $( ".boolean-field" ).change(
        function( ) {
            $.fn.changeCheckBox( $( this) );
        }
    );

    $('.change_role').click(function(){
        $.ajax({
            url:$URL_ROOT + 'ajax/change_role',
            data: JSON.stringify({
                'role_id': $(this).data('role_id')
            }),
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function(response) {
                response = JSON.parse(response);
                if(response.success) {
                    alert('role changed');
                } else {
                    alert('role not changed, user may not have permission for that role, contact an administrator');
                }
            }
        });

    });
} );

( function( $ ) {
    $.fn.addChildTableRow = function( ele ) {
        var target = ele.attr( "target_table" );
        var table_object_id = ele.attr( "table_object_id" );
        var link_column = $( "#hidden_linkcolumn_" + table_object_id ).val( );
        var new_id;
        var parser = location;
        var parent_id;
        var row_id;
        var td;
        var path = parser.pathname.split( "/" );
        if ( path[ path.length - 1 ] == "" )
            parent_id = path[ path.length - 2 ];
        else
            parent_id = path[ path.length - 1 ];

        $( "#" + target + " tr:last" ).clone( ).find( "input, select" ).each(
            function() {
		        var id = $(this).attr( 'id' );
		        var matches = id.match( /(\S+)_(\S+)_(\d+)/);

		        if ( matches[ 1 ] == 'child' ) {
		            row_id = parseInt( matches[ 3 ] )+ 1;
                    td = $( this ).closest( 'td' );

                    var old_id = "hidden_" + matches[ 2 ] + "_" + ( matches[ 3 ] );
                    var new_id = "child_" + matches[ 2 ] + "_" + ( row_id );
                    var hidden_id = "hidden_" + matches[ 2 ] + "_" + ( row_id );

		            var old_ctrl;
                    if ( td.find( '#' + old_id ).length )
                        old_ctrl = td.find( '#' + old_id );
                    else
                        old_ctrl = 0;

                    if ( link_column == matches[ 1 ] )
                        $( this ).val( parent_id ).attr( 'id', new_id ).attr( 'name', new_id );
                    else
                        $( this ).val( '' ).attr( 'id', new_id ).attr( 'name', new_id );

                    if ( matches[ 1 ] == 'name' ) {
                        td.append( "<input id='" + hidden_id + "' name='" + hidden_id + "' type='hidden' value='new'>" );
                        if ( old_ctrl )
                            old_ctrl.val( 'new' ).attr( 'id', 'hidden_row_name_' + row_id ).attr( 'name', 'hidden_row_name_' + row_id );
                        else
                            td.append( "<input id='hidden_row_name_" + row_id + "' name='hidden_row_name_" + row_id + "' type='hidden' value='new'>" );
                    } else {
                        var input_value = '';
                        if ( link_column == matches[ 1 ] )
                            input_value = parent_id;

                        if ( old_ctrl ){
                            old_ctrl.val( input_value ).attr( 'id', hidden_id ).attr( 'name', hidden_id );
                        } else {
                            td.append( "<input id='" + hidden_id + "' name='" + hidden_id + "' type='hidden' value='" + input_value + "'>" );
                        }
                    }

                    var searchbutton = $( td ).find( '.search-button' );
                    if ( searchbutton.length ) {
                        $( searchbutton ).click(
                            function( ) {
                                $.fn.searchClick( $( this ) );
                            }
                        );
                        var luid = $( this ).attr( "id" )
                        $( searchbutton ).attr( "luid", luid )
                    }

                    if ( $( this ).hasClass( 'datepicker-field' ) ) {
                        $( this ).datepicker({
                            format: 'yyyy-mm-dd',
                            autoclose: true

                        });
                    }

                    if ( $( this ).hasClass( 'lookupfield' ) ) {
                        $( this ).keydown(
                            function ( e ) {
                                return $.fn.keydownLookupField( e );
                            }
                        );
                    }

                    if ( $( this ).hasClass( 'boolean-field' ) ) {
                        $( this ).click(
                            function( ) {
                                $.fn.changeCheckBox( $( this ) );
                            }
                        );
                    }
                }
            }
        ).end( ).appendTo( "#" + target );
        td.append( "<input id='hidden_table_name_" + row_id +"' name='hidden_table_name_" + row_id +"' type='hidden' value='" + target + "'>" );
        td.append( "<input id='hidden_table_id_" + row_id +"' name='hidden_table_id_" + row_id +"' type='hidden' value='" + table_object_id + "'>" );
    }

    $.fn.showModalDialog = function ( url, buttons, callback ) {
        $("#modal_dialog_content").html("");

        $.ajax( {
            url: url,
            success: function ( resp ) {
                tmpform = resp;
                tmpform += "<div class='modal-footer'>";

                if ( buttons ) {
                    for (var key in buttons){
                        tmpform += "<button id='"+key+"' type='button' class='btn btn-default'>"+key+"</button>";
                    }
                }

                tmpform += "<button type='button' class='btn btn-default close_modal'>Close</button>";

                tmpform += "</div>";

                $(tmpform).appendTo("#modal_dialog_content");

                $( '.close_modal' ).click( $.fn.modal_close );

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

    $.fn.changeCheckBox = function ( ele ) {
        hidden_id = 'bool_' + ele.attr( 'id' );
        if ( ele.is(':checked') ) {
            $( "#" + hidden_id ).attr( 'disabled', 'disabled' );
            $( "#" + hidden_id ).val( 'y' )
        } else {
            $( "#" + hidden_id ).removeAttr( 'disabled' );
            $( "#" + hidden_id ).val( 'n' )
        }
    }

    $.fn.addLookup = function ( ele ) {
        var spancls = "ui-icon ui-icon-search search-button"
        var spanstl = "display: inline-block;float:right;"
        $('<span class="'+spancls+'" style="'+spanstl+'" luid="'+ele.attr('id')+'"/>').appendTo(ele.parent());
    }

    $.fn.keydownLookupField = function ( e, ele ) {
        var key = e.which;
        if(key == 13)  // the enter key code
        {
            var input_id = ele.attr( 'id' );
            var matches;
            var table_object;

            if ( input_id.substring( 0, 5 ) == 'child' ) {
                matches = input_id.match( /child_(\S+)_(\d+)/);
                table_object = ele.closest( 'tr' ).attr( 'table_object_name' );
            } else {
                matches = input_id.match( /(\S+)_(\d+)/);
                table_object = $( '#table_object_0' ).val( );
            }

            var module = $( '#module_0' ).val( );
            var field_name = matches[ 1 ];
            var search_vals = {};

            search_vals['search_name'] = ele.val();
            search_vals['modal_input_id'] = input_id;
            search_vals['modal_table_object'] = table_object;
            search_vals['modal_field_name'] = field_name;
            search_vals['modal_module'] = module;
            search_vals['modal_search_table'] = '';
            search_vals['modal_search_module'] = '';

            var formurl = $URL_ROOT + "core/search_results?search_vals=" + JSON.stringify(search_vals);

            $.fn.showModalDialog( formurl, {}, $.fn.searchLinks );

            return false;
        }
    }

    $.fn.searchClick = function ( ele ) {
        var input_id = ele.attr( 'luid' );
        var matches;
        var table_object;

        if ( input_id.substring( 0, 5 ) == 'child' ) {
            matches = input_id.match( /child_(\S+)_(\d+)/);
            table_object = ele.closest( 'tr' ).attr( 'table_object_name' );
        } else {
            matches = input_id.match( /(\S+)_(\d+)/);
            table_object = $( '#table_object_0' ).val( );
        }

        var field_name = matches[ 1 ];
        var module = $( '#module_0' ).val( );

        var formurl = $URL_ROOT + "core/search?table_object=" + table_object + "&input_id=" + input_id + "&field_name=" + field_name + "&module=" + module;

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


        var formurl = $URL_ROOT + "core/search_results?search_vals=" + JSON.stringify(search_vals);

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

    $.fn.modal_close = function () {
        $("#dialog").modal( "hide" );
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
    }
} ) ( jQuery );
