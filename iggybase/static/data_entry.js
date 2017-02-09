var search_open = false;
var search_input = '';

$( document ).ready( function () {
    $('input').tooltip({placement:'bottom'});
    // scroll to errors to ensure they are not hidden on scrollable x
    var errors = document.getElementsByClassName('has-error');
    for (var i = 0; i < errors.length; i++) {
        errors[i].scrollIntoView();
    }

    var cm = [ {'Fill Down': { onclick:function( menuItem, menu ) { $.fn.childDataFill( $( this ) ); } } } ];

    $.fn.addInputEvents()

    $( ".sequence_length" ).each(
        function( ) {
            $.fn.addSequenceLabel( $( this ) );
        }
    );
    $( ".sequence_length" ).keyup(
        function( e ) {
            $.fn.getSequenceLength( e, $( this ) );
        }
    );
    $( ".add_new_child_item" ).click(
        function( ) {
            $.fn.addChildTableRow( $( this ) );
        }
    );
    $( ".remove-row" ).click(
        function( ) {
            $.fn.removeRow( $( this ) );
        }
    );
    $( ".multi-row-data" ).on( 'scroll',
        function( ) {
            $.fn.updateScrollBar( $( this ) )
        }
    );
    $( ".multi-row-entry" ).find( "input, select, textarea" ).each( function( ) {
        if ( ! $( this ).is('[readonly]') ) {
            $( this ).contextMenu( cm, { theme: 'human' } );
        }
    });
} );

( function( $ ) {
    $.fn.addInputEvents = function () {
        $( document ).off( "change", ".boolean-field" );
        $( document ).on( "change", ".boolean-field", function ( ) {
            $.fn.changeCheckBox( $( this ) );
        } );

        $( document ).off( "change", ".set_price" );
        $( document ).on( "change", ".set_price", function ( e ) {
            $.fn.setPrice( e, $( this ) );
        } );

        $( document ).off( "change", ".field_select_list" );

        $( document ).off( "blur", ".charge-method-code" );
        $( document ).on( "blur", ".charge-method-code", function() {
            $.fn.checkCodeFormat( $( this ) );
        } );

        $( document ).off( "blur", ".charge-method-percent" );
        $( document ).on( "blur", ".charge-method-percent", function( e ) {
            $.fn.checkCodePercent( e, $( this ) );
        } );

        $( document ).off( "keydown focusout", ".table-control" );
        $( document ).on( "keydown focusout", ".table-control", function ( e ) {
            return $.fn.dataEntryEventManager( e, $( this ) );
        } );


        $( document ).off( "keydown focusout", ".data-control" );
        $( document ).on( "keydown focusout", ".data-control", function ( e ) {
            return $.fn.dataEntryEventManager( e, $( this ) );
        } );

    }

    $.fn.addSequenceLabel = function ( ele ) {
        $('<label id="label_'+ele.attr('id')+'" class="control-label">Sequence Length: '+(ele.val().length)+'</label>').appendTo(ele.parent());
    }

    $.fn.getSequenceLength = function ( e, ele ) {
        $( '#label_'+ele.attr('id') ).text( 'Sequence Length: '+(ele.val().length) );
    }

    $.fn.setPrice = function ( e, ele ) {
        var price_item = ele.val();
        var row_sibs = ele.parent().parent().siblings();
        var hidden_fields = $("#hidden_fields");

        var table_name = hidden_fields.find('input[name=table]').val();
        var facility = hidden_fields.find('input[name=facility]').val();
        // TODO: use org id to get price_type
        var criteria = {'price_item_id': price_item};
        var fields = ['price_per_unit'];
        var url = $URL_ROOT + facility + '/billing/get_price/ajax';
        $.ajax({
            // TODO: put facility in hidden fields and access dynamically
            url: url,
            data: JSON.stringify({
                'criteria': criteria,
                'fields': fields
            }),
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function(response) {
                response = JSON.parse(response);
                if(response.price_per_unit.length > 0) {
                    price = parseFloat(response.price_per_unit);
                    row_sibs.each(function() {
                        var price_ele = $(this).find("[id^='data_entry_price_per_unit']");
                        if (price_ele.length > 0) {
                            $(price_ele).val(price);
                        }
                    });

                }
            }
        });
    }

    $.fn.dataEntryEventManager = function ( e, ele ) {
        var ele_class = ele.attr( 'class' );

        if ( e.keyCode == 13 ) {
            e.preventDefault( );

            if ( ele_class.includes( 'lookupfield' ) && !search_open ) {
                if ( ele.val() )
                    return $.fn.searchResults( ele, false );
                else
                    $( "#id_" + ele.attr( 'id' ) ).val( '' );
            }

            return false;
        } else if ( ele_class.includes( 'lookupfield' ) && e.type == "focusout" && !search_open ) {
            if ( ele.val() )
                return $.fn.searchResults( ele, false );
            else
                $( "#id_" + ele.attr( 'id' ) ).val( '' );
        }
    }

    $.fn.searchResults = function ( ele, modal_open, search_vals ) {
        search_input = ele.attr( 'id' );

        var matches = search_input.match( /data_entry_(\S+)_(\d+)/);
        var table_object = $( '#record_data_table_' + matches[2] ).val( );

        if ( !search_vals )
            var search_vals = {};

        search_vals['table_name'] = table_object;
        search_vals['input_id'] = search_input;
        search_vals['display_name'] = matches[ 1 ];
        search_vals['value'] = ele.val( );
        search_vals['by_field'] = ele.val( );
        search_vals['field_key'] = table_object + "|" + matches[ 1 ];
        search_vals['modal_open'] = modal_open;

        var hidden_fields = $("#hidden_fields");
        search_vals['facility'] = hidden_fields.find('input[name=facility]').val()
        var url = $URL_ROOT + search_vals['facility'] + "/core/search_results?search_vals=" + JSON.stringify(search_vals);

        $.ajax({
            url: url,
            type: 'POST',
            success: function(response) {
                var results = JSON.parse(response);
                if ( results[0] == 1 ) {
                    $( "#" + search_input ).val( results[1] );
                    $( "#id_" + search_input ).val( results[2] );

                    return false;
                } else {
                    $( "#" + search_input ).val( '' );
                    $( "#id_" + search_input ).val( '' );

                    if ( modal_open )
                        $.fn.displaySearchResults( results );
                    else {
                        $.fn.searchModal( ele, results, search_vals );
                    }
                }
            }
        });
    }

    $.fn.searchModal = function ( ele, search_results, search_vals ) {
        var formurl = $URL_ROOT + search_vals['facility'] + "/core/search?search_vals=" +  JSON.stringify(search_vals);

        var buttons = {};
        buttons[ "Search" ] = {'function': $.fn.getSearchResults, 'append_to': 'modal_top_buttons'};

        var callback = function () {
            $.fn.displaySearchResults( search_results );
        };

        $.fn.showModalDialog( $( '#search-dialog' ), $( '#modal_search_content' ), formurl, buttons, callback, $.fn.searchClose );
    }

    $.fn.getSearchResults = function ( ) {
        search_vals = {};

        $(".search-body input").each(function() {
            search_vals[$(this).attr('id')] = $(this).val();
        });

        var search_results = $.fn.searchResults( $( "#" + search_input ), true, search_vals );

        $.fn.displaySearchResults( search_results );
    }

    $.fn.displaySearchResults = function ( search_results ) {
        search_open = true;

        $( "#modal_search_results" ).empty();

        $( "#modal_search_results" ).append( search_results );

        $( ".search-results" ).click( function( ){ $.fn.searchUpdate( $(this) ); } );
    }

    $.fn.searchUpdate = function ( ele ) {
        var input_id = $( "#modal_input_id" ).val( );

        $( "#" + input_id ).val( ele.val( ) );
        $( "#id_" + input_id ).val( ele.attr( 'val_id' ) );

        $.fn.searchClose( );
    }

    $.fn.searchClose = function ( ele ) {
        search_open = false;

        $("#search-dialog").modal( "hide" );
        //$('body').removeClass('modal-open');
        //$('.modal-backdrop').remove();
        $("#modal_search_content").html("");
    }

    $.fn.addChildTableRow = function( ele ) {
        var target = ele.attr( "target_table" );
        var table_level = ele.attr( "table_level" );
        var table_object_id = ele.attr( "table_object_id" );
        var link_column = $( "#linkcolumn_" + table_object_id ).val( );
        var new_row = $( "#" + target + " .row:last" ).clone( );
        var old_id = new_row.attr( 'row_id' );
        var parent_name = '';
        var parent_id = '';
        var new_id = '';
        if ( table_level == 1 )
            parent_name = $( '#record_data_row_name_0' ).val( );
            parent_id = $( '#data_entry_id_0' ).val( );

        //alert('table_level: ' + table_level);
        //alert('parent_name: ' + parent_name);
        //alert('link_column: ' + link_column);

        var row_id = parseInt( $( '#row_counter' ).val( ) ) + 1;
        $( '#row_counter' ).val( parseInt( row_id ) );

        new_row.attr( 'row_id', row_id );

        var values = new Array();
        var inputs = new Array();

        if ( new_row.has( 'new-row' ).length < 1 )
            new_row.addClass( 'new-row' );

        if ( new_row.has( '.remove-row' ).length < 1 )
            new_row.prepend('<span data_row_id="' + row_id + '" class="glyphicon glyphicon-minus remove-row"></span>');

        new_row.find( '.spacer-15' ).remove();

        new_row.find( "input, select" ).each(
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

        $( new_row ).on( 'click', '.remove-row', function ( ) { $.fn.removeRow( $( this ) ); } );

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
                    } else if ( matches[ 1 ] == 'record_data_new' ) {
                        value = 1;
                    } else if ( matches[ 1 ] == 'id_data_entry_' + link_column ) {
                        value = parent_id;
                    }

                    var new_input = $( '<input>' ).attr( {
                        style: 'display:none;',
                        id: new_id,
                        name: new_id,
                        value: value
                    } ).appendTo( new_row );
                }
            }
        );

        new_row.find( '.boolean-field' ).each(
            function() {
                $.fn.changeCheckBox( $( this ) );
                $.fn.updateOldValue( $( this ) );
            }
        );

        new_row.find( '.lookupfield' ).each(
            function ( ) {
                $( '<input>' ).attr( {
                    style: 'display:none;',
                    id: 'id_' + new_id,
                    name: 'id_' + new_id
                } ).appendTo( new_row );
            }
        );

        $.fn.addInputEvents()
    }

    $.fn.removeRow = function ( ele ) {
        var row_id = $( ele ).attr( 'data_row_id' );
        alert(row_id);

        $("input[id$='_" + row_id + "']").remove( );
        $( ele ).closest( '.row' ).remove( );
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

    $.fn.updateOldValue = function ( ele ) {
        id = ele.attr( 'id' );
        new_id = id.replace( 'data_entry', 'old_value' );
        if ( ele.attr( 'value' ) == 'y' )
            $( "#" + new_id ).attr( 'value', 'True' );
        else
            $( "#" + new_id ).attr( 'value', 'False' );
    }

    $.fn.childDataFill = function ( ae ) {
        var value = ae.val();
        var check = false;

        if ( ae.attr( "type" ) == "checkbox" ) {
            check = true;
            value = ae.is( ":checked" ) ? true : false;
        }

        var cont = true
        var current_row = ae.closest( 'div.row' );

        var id = ae.attr( 'id' );
        var matches = id.match( /(\S+)_(\d+)/);
        var id_prefix = matches[ 1 ];

        while ( current_row.next('div.row').length ){
            current_row = current_row.next('div.row');
            current_row_number = current_row.attr( 'row_id' );

            new_id = id_prefix + '_' + current_row_number

            if ( check ) {
                $( "#" + new_id ).prop( "checked", value );
                $( "input[name=bool_" + new_id + "]" ).prop( 'disabled', value );
                $( "input[name=bool_" + new_id + "]" ).val( value ? 'y' : 'n' );
            } else if ( $( "#" + new_id ).closest( "div.row" ).is( ":visible" ) ) {
                $( "#" + new_id ).val( value );
                $( "#" + new_id ).change( );
            }
        }
    }

    $.fn.updateScrollBar = function( data_div ) {
        var table_name = data_div.attr( 'name' );

        $( '#' + table_name + '_header' ).scrollLeft( data_div.scrollLeft( ) )
    }
} ) ( jQuery );
