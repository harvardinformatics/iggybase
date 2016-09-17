$( document ).ready( function () {
    if (formErrors) {
        $('#dialog').modal('show');
    }
    $( ".lookupfield" ).each(
        function( ) {
            $.fn.addLookup( $( this ) );
        }
    );
    $( ".modal-add" ).click(
        function( ) {
            $.fn.modalAdd( $( this ) );
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
    $( "form .lookupfield" ).on( "keydown focusout",
        function ( e ) {
            return $.fn.lookupField( e, $( this ) );
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

    var cm = [ {'Fill Down': { onclick:function( menuItem, menu ) { $.fn.childDataFill( $( this ) ); } } } ];

    $( ".multiline-table" ).find( "input" ).each( function( ) {
        if ( ! $( this ).is('[readonly]') ) {
            $( this ).contextMenu( cm, { theme: 'human' } );
        }
    });

    $( ".multiline-table" ).find( "select" ).each( function( ) {
        $( this ).contextMenu( cm, { theme: 'human' } );
    });

    $( ".multiline-table" ).find( "textarea" ).each( function( ) {
        $( this ).contextMenu( cm, { theme: 'human' } );
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
        var new_id = '';
        if ( table_level == 1 )
            parent_name = $( '#record_data_row_name_0' ).val( );

        //alert('table_level: ' + table_level);
        //alert('parent_name: ' + parent_name);
        //alert('link_column: ' + link_column);

        var row_id = parseInt( $( '#row_counter' ).val( ) ) + 1;
        $( '#row_counter' ).val( parseInt( row_id ) );

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
                            //alert('select matches[ 1 ]: ' + matches[ 1 ]);
                            if ( 'data_entry_' + link_column == matches[ 1 ] ) {
                                //alert('looking for: ' + parent_name);
                                $( this ).attr( 'id', new_id ).attr( 'name', new_id )
                                $( this ).find( 'option' ).each(
                                    function( index, element ) {
                                        if ( element.text == parent_name ){
                                            $( element ).attr( 'selected', true );
                                        }
                                    }
                                );
                                //alert('new_id: ' + new_id);
                            } else {
                                $( this ).prop( 'selectedIndex', 0 ).attr( 'id', new_id ).attr( 'name', new_id );
                            }
                        } else {
                            if ( 'data_entry_' + link_column == matches[ 1 ] )
                                $( this ).val( parent_name ).attr( 'id', new_id ).attr( 'name', new_id );
                            else if ( $( this ).attr( 'class' ).includes( 'date-field' ) ) {
                                var utc = new Date().toJSON().slice(0,10);
                                $( this ).val( utc ).attr( 'id', new_id ).attr( 'name', new_id );
                            } else
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
                    new_id = matches[ 1 ] + "_" + ( row_id );
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

                $( '<input>' ).attr( {
                    style: 'display:none;',
                    id: 'id_' + new_id,
                    name: 'id_' + new_id
                } ).appendTo( new_tr );
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
            $( '#data_entry_foreign_key_field_id_' + row_id ).attr( 'value', '' );
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

    $.fn.modalAdd = function ( ele ) {
        var table_name = ele.attr( 'table_name' );

        var hidden_fields = $("#hidden_fields");
        var facility = hidden_fields.find('input[name=facility]').val()
        var formurl = $URL_ROOT + facility + "/core/modal_add/" + table_name;

        var buttons = {};

        $.fn.showModalDialog( formurl, buttons );

        $( document ).on("click", "#modal-add-submit", function() {
            $.fn.modalAddSubmit( )
        } );
    }

    $.fn.modalAddSubmit = function ( ) {
        var table_name = $("#record_data_table_0").val( );
        var form_data = new FormData();
        var hidden_fields = $("#hidden_fields");
        var facility = hidden_fields.find('input[name=facility]').val();

        $("#div-modal :input:not(:checkbox):not(:button)").each(
            function() {;
                if ( typeof $( this ).attr( 'id' ) != 'undefined' ) {
                    if ( typeof $( this ).val( ) != 'undefined' ) {
                        if ( $( this ).attr( 'id' ) == 'file ' ) {
                            form_data.append( $( this ).attr( 'id' ), $( this )[0].files[0] );
                        } else {
                            form_data.append( $( this ).attr( 'id' ), $( this ).val( ) );
                        }
                    }
                }
            }
        );

        $.ajax({
            url:$URL_ROOT + facility + '/core/modal_add_submit/' + table_name,
            data: form_data,
            contentType: false,
            processData: false,
            type: 'POST',
            success: function(response) {
                response = JSON.parse(response);
                if(response.error) {
                    alert(response.errors);
                } else {
                    $.fn.modal_close( );
                    $("#modal_dialog_content").html("");
                }
            }
        });
    }

    $.fn.lookupField = function ( e, ele ) {
        if( e.keyCode == 13 || e.type == "focusout" )  // the enter key code
        {
            if ( e.keyCode == 13 ) {
                ele.off("focusout")
            }
            var input_id = ele.attr( 'id' );

            var matches = input_id.match( /data_entry_(\S+)_(\d+)/);
            var table_object = $( '#record_data_table_' + matches[2] ).val( );

            var display_name = matches[ 1 ];
            var search_vals = {};

            search_vals['search_by_field'] = ele.val();
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
        $( "#" + ele.attr('luid') ).on( "focusout",
            function ( e ) {
                return $.fn.lookupField( e, $( this ) );
            }
        );
        $("#" + ele.attr('luid')).val(ele.val());
        $("#id_" + ele.attr('luid')).val(ele.attr('val_id'));
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

    $.fn.childDataFill = function ( ae ) {
        if ( ae.attr( "type" ) == "checkbox" ) {
            var check = true;
            var value = ae.is( ":checked" ) ? true : false;
        } else {
            var value = ae.val();
            var check = false;
        }

        var cont = true;
        var id = ae.attr( 'id' );
        var matches = id.match( /(\S+)_(\d+)/);
        var i = matches[ 2 ];
        var type = ae.get(0).tagName;
        var well = false;
        var index = false;

        var prefix = "";
        var row;
        var col;

        if ( id.match( /Child_Well(\S+)_(\d+)/ ) && value != "" ) {
            well = true;
            row = value.substring( 0, 1 ).toUpperCase( );
            col = parseInt( value.substring( 1, 3 ) );
        } else if ( id.match( /Child_Index(\S+)_(\d+)/ ) && value != "" ) {
            var wellid = value.substr( value.length - 3, value.length + 1 );

            if ( wellid.match( /[A-H][0-1][0-9]/ ) ) {
                well = true;

                if ( wellid != value ) {
                    matches = value.match( /(\S*)(\s*)(\S)(\d*)/ )
                    prefix = matches[ 1 ] + matches[ 2 ];
                }

                row = wellid.substring( 0, 1 ).toUpperCase( );
                col = parseInt( wellid.substring( 1, 3 ) );
            } else {
                index = true;
                matches = value.match( /(\S*)(\s*)(\d*)/ )
                prefix = matches[ 1 ] + matches[ 2 ];
                col = parseInt( matches[ 3 ] );
            }
        }

        while ( cont ){
            i++;
            id = id.replace(/(\S+)_(\d+)/,'$1' + '_' + i );

            if ( check ) {
                $( type + "[id='" + id + "'].value" ).prop( "checked", value );
                $( "input[id='" + id + "'].novalue" ).prop('disabled', value);
            }else if ( well ) {
                row = String.fromCharCode( row.charCodeAt( 0 ) + 1 );

                if ( row == "I" ) {
                    row = "A";
                    col++;
                }

                if ( col < 10 )
                    value = prefix + row + "0" + col;
                else
                    value = prefix + row + col;
            } else if ( index ) {
                col++;
                if ( col < 10 )
                    value = prefix + "0" + col;
                else
                    value = prefix + col;
            }

            if ( $( type + "[id='" + id + "']" ).length > 0 ) {
                if ( !check && $( type + "[id='" + id + "']" ).closest( "tr" ).is( ":visible" ) ) {
                    $( type + "[id='" + id + "']" ).val( value );
                    $( type + "[id='" + id + "']" ).change( );
                }
            } else {
                cont = false;
            }
        }
    }

} ) ( jQuery );
