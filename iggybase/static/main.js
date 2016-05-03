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
        var currenturl = $.fn.parseURL(document.URL);
        var paths = currenturl.pathname.split("/");
        var newpath = $URL_ROOT + $(this).data('facility') + "/";

        $.ajax({
            url:$URL_ROOT + paths[1] + '/core/change_role',
            data: JSON.stringify({
                'role_id': $(this).data('role_id')
            }),
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function(response) {
                response = JSON.parse(response);
                if(response.success) {
                    alert('role changed');

                    //pathname starts with / facility in index 1
                    for (var i=2;i<paths.length;i++)
                        if (paths[i] != '')
                            newpath += paths[i]+"/";

                    window.location.href = newpath.slice(0, -1)+currenturl.search;
                } else {
                    alert('role not changed, user may not have permission for that role, contact an administrator');
                }
            }
        });

        //will not work without this
        return false;
    });
} );

( function( $ ) {
    $.fn.addChildTableRow = function( ele ) {
        var target = ele.attr( "target_table" );
        var table_object_id = ele.attr( "table_object_id" );
        var link_column = $( "#linkcolumn_" + table_object_id ).val( );
        var parent_name = $( '#old_value_name_1' ).val( );

        var old_id;
        var row_id;

        var new_tr = $( "#" + target + " tr:last" ).clone( )

        new_tr.find( "input, select" ).each(
            function() {
		        var id = $(this).attr( 'id' );
		        var matches = id.match( /(\S+)_(\d+)/);

		        if ( matches && matches.length > 1 ) {
		            old_id = matches[ 2 ];
		            row_id = parseInt( matches[ 2 ] )+ 1;
                    var td = $( this ).closest( 'td' );

                    var new_id = matches[ 1 ] + "_" + ( row_id );

                    if ( $( this ).prop( 'type' ) == 'select-one' ) {
                        if ( 'data_entry_' + link_column == matches[ 1 ] ) {
                            $( this ).attr( 'id', new_id ).attr( 'name', new_id );
                            $( this ).filter( function( ) { return $( this ).text( ) == parent_name; } ).prop( 'selectedIndex', true );
                        } else {
                            $( this ).prop( 'selectedIndex', 0 ).attr( 'id', new_id ).attr( 'name', new_id );
                        }
                    } else {
                        if ( 'data_entry_' + link_column == matches[ 1 ] )
                            $( this ).val( parent_name ).attr( 'id', new_id ).attr( 'name', new_id );
                        else
                            $( this ).val( '' ).attr( 'id', new_id ).attr( 'name', new_id );
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
                        $( this ).change(
                            function( ) {
                                $.fn.changeCheckBox( $( this ) );
                            }
                        );
                    }
                }
            }
        ).end( ).appendTo( "#" + target );

        var values = new Array();
        var inputs = new Array();

        $('input[id$="_' + old_id + '"]' ).each(
            function() {
                if ( $( this ).css( 'display' ) == 'none' ) {
                    var matches = $( this ).attr( 'id' ).match( /(\S+)_(\d+)/);
                    var new_id = matches[ 1 ] + "_" + ( row_id );
                    var value = '';

                    var new_input = $( '<input>' ).attr( {
                        type: 'hidden',
                        id: new_id,
                        name: new_id
                    } ).appendTo( new_tr );

                    if ( matches[ 1 ] == 'old_value_name' || matches[ 1 ] == 'record_data_row_name' ) {
                        values[values.length] = 'new';
                        inputs[inputs.length] = new_id
                    } else if ( matches[ 1 ] == 'record_data_table_id' ) {
                        values[values.length] = table_object_id;
                        inputs[inputs.length] = new_id
                    } else if ( matches[ 1 ] == 'record_data_table_name' ) {
                        values[values.length] = target;
                        inputs[inputs.length] = new_id
                    } else if ( 'old_value_' + link_column == matches[ 1 ] ) {
                        values[values.length] = $( this ).val();
                        inputs[inputs.length] = new_id
                    }
                }
            }
        )

        for ( var i = 0; i < values.length; i++ )
            document.getElementsByName( inputs[ i ] )[ 0 ].value = values[ i ];
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

            var display_name = matches[ 1 ];
            var search_vals = {};

            search_vals['search_name'] = ele.val();
            search_vals['modal_input_id'] = input_id;
            search_vals['modal_table_object'] = table_object;
            search_vals['modal_field_name'] = display_name;
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

        var display_name = matches[ 1 ];

        var formurl = $URL_ROOT + "system/core/search?table_object=" + table_object + "&input_id=" + input_id + "&field_name=" + display_name;

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
