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
    $( ".field_select_list" ).change(
        function( ) {
            $.fn.updateTableField( $( this ) )
        }
    );

    $('.disabled').click(function(e){
        e.preventDefault();
    });

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
        var table_level = ele.attr( "table_level" );
        var table_object_id = ele.attr( "table_object_id" );
        var link_column = $( "#linkcolumn_" + table_object_id ).val( );
        var new_tr = $( "#" + target + " tr:last" ).clone( );
        var old_id = new_tr.attr( 'row_id' );
        var parent_name = '';
        if ( table_level == 1 )
            parent_name = $( '#record_data_row_name_0' ).val( );

        var row_id = $( '#row_counter' ).val( );
        $( '#row_counter' ).val( parseInt( row_id ) + 1 );

        new_tr.attr( 'row_id', row_id );

        var values = new Array();
        var inputs = new Array();

        new_tr.find( "input, select" ).each(
            function() {
                if ( $( this ).css( 'display' ) == 'none' ) {
                    $( this ).remove( );
                } else {
                    var id = $(this).attr( 'id' );
                    var matches = id.match( /(\S+)_(\d+)/ );

                    if ( matches && matches.length > 1 ) {
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
                    }
                }
            }
        ).end( ).appendTo( "#" + target );

        $('input[id$="_' + old_id + '"]' ).each(
            function() {
                if ( $( this ).css( 'display' ) == 'none' ) {
                    var matches = $( this ).attr( 'id' ).match( /(\S+)_(\d+)/);
                    var new_id = matches[ 1 ] + "_" + ( row_id );
                    var value = '';

                    if ( matches[ 1 ] == 'record_data_row_name' ) {
                        value = 'new';
                    } else if ( matches[ 1 ] == 'record_data_table_id' ) {
                        value = table_object_id;
                    } else if ( matches[ 1 ] == 'record_data_table' ) {
                        value = target;
                    }

                    var new_input = $( '<input>' ).attr( {
                        style: 'display:none;',
                        id: new_id,
                        name: new_id,
                        value: value
                    } ).appendTo( new_tr );
                }
            }
        )

        new_tr.find( '.search-button' ).each(
            function() {
                $( this ).click(
                    function( ) {
                        $.fn.searchClick( $( this ) );
                    }
                );
                var luid = $( this ).attr( "luid" ).match( /(\S+)_(\d+)/);
                var new_luid = luid[ 1 ] + "_" + row_id
                var id = $( this ).attr( "id" ).match( /(\S+)_(\d+)/);
                var new_id = id[ 1 ] + "_" + row_id
                $( this ).attr( "luid", new_luid ).attr( "id", new_id ).attr( "name",  new_id );
            }
        );

        new_tr.find( '.boolean-field' ).change(
            function() {
                $( this ).change(
                    function( ) {
                        $.fn.changeCheckBox( $( this ) );
                    }
                );
            }
        ).each(
            function() {
                $.fn.changeCheckBox( $( this ) );
                $.fn.updateOldValue( $( this ) );
            }
        );

        new_tr.find( '.datepicker-field' ).each(
            function() {
                $( this ).datepicker({
                    format: 'yyyy-mm-dd',
                    autoclose: true

                });
            }
        );

        new_tr.find( '.lookupfield' ).each(
            function() {
                $( this ).keydown(
                    function ( e ) {
                        return $.fn.keydownLookupField( e, $( this ) );
                    }
                );
            }
        );

        new_tr.find( ".field_select_list" ).change(
            function( ) {
                $.fn.updateTableField( $( this ) )
            }
        );
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
            $( "#" + ele.attr( 'id' ) ).attr( 'value', 'y' );
            $( "#" + bool_id ).attr( 'value', 'y' );
            $( "#" + bool_id ).attr( 'disabled', 'disabled' );
        } else {
            $( "#" + ele.attr( 'id' ) ).attr( 'value', 'n' );
            $( "#" + bool_id ).attr( 'value', 'n' );
            $( "#" + bool_id ).removeAttr( 'disabled' );
        }
    }

    $.fn.updateTableField = function ( ele ) {
        var id = ele.attr( 'id' );
        var matches = id.match( /data_entry_(\S+)_(\d+)/);
        var row_id = matches[ 2 ];
        input_type = ele.is( 'input' );

        if ( ( input_type && ele.attr( 'value' ) == '' ) ||
                    ( !input_type && $( '#' + id + ' option:selected' ).text( ) == '' ) ) {
            $( '#data_entry_foreign_key_table_object_id_' + row_id ).attr( 'readonly', false );
            $( '#data_entry_foreign_key_field_id_' + row_id ).attr( 'readonly', false );
            $( '#data_entry_foreign_key_display_' + row_id ).attr( 'readonly', false );
            $( '#data_entry_foreign_key_table_object_id_' + row_id ).attr( 'value', '' );
            $( '#data_entry_foreign_key_field_id_' + row_id ).attr( 'value', '' );
            $( '#data_entry_foreign_key_display_' + row_id ).attr( 'value', '' );
            $( "#span_foreign_key_table_object_id_"+row_id ).css( "pointer-events", "auto" );
            $( "#span_foreign_key_field_id_"+row_id ).css( "pointer-events", "auto" );
            $( "#span_foreign_key_display_"+row_id ).css( "pointer-events", "auto" );
        } else {
            $( '#data_entry_foreign_key_table_object_id_' + row_id ).attr( 'readonly', true );
            $( '#data_entry_foreign_key_field_id_' + row_id ).attr( 'readonly', true );
            $( '#data_entry_foreign_key_display_' + row_id ).attr( 'readonly', true );
            $( '#data_entry_foreign_key_table_object_id_' + row_id ).attr( 'value', 'select_list_item' );
            $( '#data_entry_foreign_key_field_id_' + row_id ).attr( 'value', 'F001501' );
            $( '#data_entry_foreign_key_display_' + row_id ).attr( 'value', '' );
            $( "#span_foreign_key_table_object_id_"+row_id ).css( "pointer-events", "none" );
            $( "#span_foreign_key_field_id_"+row_id ).css( "pointer-events", "none" );
            $( "#span_foreign_key_display_"+row_id ).css( "pointer-events", "none" );
        }
    }

    $.fn.updateOldValue = function ( ele ) {
        id = ele.attr( 'id' );
        new_id = id.replace( 'data_entry', 'old_value' );
        if ( ele.attr( 'value' ) == 'y' )
            $( "#" + new_id ).attr( 'value', 'True' );
        else
            $( "#" + new_id ).attr( 'value', 'False' );
    }

    $.fn.addLookup = function ( ele ) {
        var id = ele.attr( 'id' );
        var matches = id.match( /data_entry_(\S+)_(\d+)/);
        var new_id = "span_" + matches[ 1 ] + "_" + matches[ 2 ];

        var spancls = "ui-icon ui-icon-search search-button";

        $('<span id="'+new_id+'" name="'+new_id+'" class="'+spancls+'" luid="'+id+'"/>').appendTo(ele.parent());
    }

    $.fn.keydownLookupField = function ( e, ele ) {
        var key = e.which;
        if(key == 13)  // the enter key code
        {
            var input_id = ele.attr( 'id' );

            var matches = input_id.match( /data_entry_(\S+)_(\d+)/);
            var table_object = $( '#record_data_table_' + matches[2] ).val( );

            var display_name = matches[ 1 ];
            var search_vals = {};

            search_vals['search_name'] = ele.val();
            search_vals['modal_input_id'] = input_id;
            search_vals['modal_table_object'] = table_object;
            search_vals['modal_field_name'] = display_name;
            search_vals['modal_search_table'] = '';

            var hidden_fields = $("#hidden_fields");
            var facility = hidden_fields.find('input[name=facility]').val()
            var formurl = $URL_ROOT + facility + "/core/search_results?search_vals=" + JSON.stringify(search_vals);

            $.fn.showModalDialog( formurl, {}, $.fn.searchLinks );

            return false;
        }
    }

    $.fn.searchClick = function ( ele ) {
        var input_id = ele.attr( 'luid' );

        var matches = input_id.match( /data_entry_(\S+)_(\d+)/);
        var table_object = $( '#record_data_table_' + matches[2] ).val( );

        var display_name = matches[ 1 ];

        var hidden_fields = $("#hidden_fields");
        var facility = hidden_fields.find('input[name=facility]').val()
        var formurl = $URL_ROOT + facility + "/core/search?table_object=" + table_object + "&input_id=" + input_id + "&field_name=" + display_name;

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

        var hidden_fields = $("#hidden_fields");
        var facility = hidden_fields.find('input[name=facility]').val()
        var formurl = $URL_ROOT + facility + "/core/search_results?search_vals=" + JSON.stringify(search_vals);

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
