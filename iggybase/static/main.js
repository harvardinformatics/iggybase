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
            $.fn.changeCheckBox( $( this ) );
        }
    );

    $('.change_role').click(function(){
        $.ajax({
            // TODO: don't hardcode facility
            url:$URL_ROOT + $(this).data('facility') + '/core/ajax/change_role',
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

        var currenturl = $.fn.parseURL(document.URL);
        var paths = currenturl.pathname.split("/");
        var newpath = currenturl.protocol+"//"+currenturl.hostname+"/"+$(this).data('facility')+"/";

        //pathname starts with / facility in index 1
        for (var i=2;i<paths.length;i++)
            if (paths[i] != '')
                newpath += paths[i]+"/";

        window.location.href = newpath.slice(0, -1)+currenturl.search;

        //will not work without this
        return false;
    });
} );

( function( $ ) {
    $.fn.addChildTableRow = function( ele ) {
        var target = ele.attr( "target_table" );
        var table_object_id = ele.attr( "table_object_id" );
        var link_column = $( "#linkcolumn_" + table_object_id ).val( );
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
		        var matches = id.match( /(\S+)_(\d+)/);

		        if ( matches && matches.length > 1 ) {
		            row_id = parseInt( matches[ 2 ] )+ 1;
                    td = $( this ).closest( 'td' );

                    //clear old hidden fields if more than 1 row was added
                    $( td ).find( 'input[type=hidden]' ).remove( );

                    var new_id = "data_entry_" + matches[ 1 ] + "_" + ( row_id );
                    var hidden_id = "old_value_" + matches[ 1 ] + "_" + ( row_id );

                    if ( $( this ).prop( 'type' ) == 'select-one' ) {
                        if ( link_column == matches[ 1 ] ) {
                            $( this ).attr( 'id', new_id ).attr( 'name', new_id );
                            $( this ).filter( function( ) { return $( this ).text( ) == parent_id; } ).prop( 'selectedIndex', true );
                        } else {
                            $( this ).prop( 'selectedIndex', 0 ).attr( 'id', new_id ).attr( 'name', new_id );
                        }
                    } else {
                        if ( link_column == matches[ 1 ] )
                            $( this ).val( parent_id ).attr( 'id', new_id ).attr( 'name', new_id );
                        else
                            $( this ).val( '' ).attr( 'id', new_id ).attr( 'name', new_id );
                    }

                    if ( matches[ 1 ] == 'name' ) {
                        td.append( "<input id='" + hidden_id + "' name='" + hidden_id + "' type='hidden' value='new'>" );
                        td.append( "<input id='record_data_row_name_" + row_id + "' name='record_data_row_name_" + row_id + "' type='hidden' value='new'>" );
                        td.append( "<input id='record_data_table_name_" + row_id +"' name='record_data_table_name_" + row_id +"' type='hidden' value='" + target + "'>" );
                        td.append( "<input id='record_data_table_id_" + row_id +"' name='record_data_table_id_" + row_id +"' type='hidden' value='" + table_object_id + "'>" );
                    } else {
                        td.append( "<input id='" + hidden_id + "' name='" + hidden_id + "' type='hidden' value=''>" );
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
                                return $.fn.keydownLookupField( e, $( this ) );
                            }
                        );
                    }

                    if ( $( this ).hasClass( 'boolean-field' ) ) {
                        new_bool_id = 'bool_' + new_id;
                        if ( $( this ).is(':checked') )
                            td.append( "<input id='" + new_bool_id + "' name='" + new_bool_id + "' type='hidden' value='y' disabled='disabled'>" );
                        else
                            td.append( "<input id='" + new_bool_id + "' name='" + new_bool_id + "' type='hidden' value='n'>" );

                        $( this ).change(
                            function( ) {
                                $.fn.changeCheckBox( $( this ) );
                            }
                        );
                    }
                }
            }
        ).end( ).appendTo( "#" + target );
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
        bool_id = 'bool_' + ele.attr( 'id' );
        if ( ele.is(':checked') ) {
            $( "#" + bool_id ).val( 'y' ).attr( 'disabled', 'disabled' );
        } else {
            $( "#" + bool_id ).val( 'n' ).removeAttr( 'disabled' );
        }
    }

    $.fn.addLookup = function ( ele ) {
        var spancls = "ui-icon ui-icon-search search-button";
        $('<span class="'+spancls+'" luid="'+ele.attr('id')+'"/>').appendTo(ele.parent());
    }

    $.fn.keydownLookupField = function ( e, ele ) {
        var key = e.which;
        if(key == 13)  // the enter key code
        {
            var input_id = ele.attr( 'id' );

            var matches = input_id.match( /data_entry_(\S+)_(\d+)/);
            var table_object = $( '#record_data_table_name_' + matches[2] ).val( );

            var field_name = matches[ 1 ];
            var search_vals = {};

            search_vals['search_name'] = ele.val();
            search_vals['modal_input_id'] = input_id;
            search_vals['modal_table_object'] = table_object;
            search_vals['modal_field_name'] = field_name;
            search_vals['modal_search_table'] = '';

            var formurl = $URL_ROOT + "system/core/search_results?search_vals=" + JSON.stringify(search_vals);

            $.fn.showModalDialog( formurl, {}, $.fn.searchLinks );

            return false;
        }
    }

    $.fn.searchClick = function ( ele ) {
        var input_id = ele.attr( 'luid' );

        var matches = input_id.match( /data_entry_(\S+)_(\d+)/);
        var table_object = $( '#record_data_table_name_' + matches[2] ).val( );

        var field_name = matches[ 1 ];

        var formurl = $URL_ROOT + "system/core/search?table_object=" + table_object + "&input_id=" + input_id + "&field_name=" + field_name;

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

        var formurl = $URL_ROOT + "system/core/search_results?search_vals=" + JSON.stringify(search_vals);

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

    $.fn.parseURL = function (url) {
        var parser = document.createElement('a'),
            searchObject = {},
            queries, split, i;
        // Let the browser do the work
        parser.href = url;
        // Convert query string to object
        queries = parser.search.replace(/^\?/, '').split('&');
        for( i = 0; i < queries.length; i++ ) {
            split = queries[i].split('=');
            searchObject[split[0]] = split[1];
        }
        return {
            protocol: parser.protocol,
            host: parser.host,
            hostname: parser.hostname,
            port: parser.port,
            pathname: parser.pathname,
            search: parser.search,
            searchObject: searchObject,
            hash: parser.hash
        };
    }
} ) ( jQuery );
