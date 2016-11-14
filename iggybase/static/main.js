var search_click = false;

$( document ).ready( function () {
    /* add a hack to get mac firefox scrollbars to show, no way in pure css */
    //constantly update the scroll position:
    sc=setInterval($.fn.scrollDown,200);
    //optional:stop the updating if it gets a click
    jQuery('.multi-row-data').mousedown(function(e){
        clearInterval(sc);
    });

    if (formErrors) {
        $('#dialog').modal('show');
    }
    $( ".modal-add" ).click(
        function( ) {
            $.fn.modalAdd( $( this ) );
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
    $.fn.showModalDialog = function ( url, buttons, callback, close_function ) {
        $("#modal_dialog_content").html("");

        $.ajax( {
            url: url,
            type: "POST",
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

                if ( close_function )
                    $( '.close_modal' ).click( close_function );
                else
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

    $.fn.modalAdd = function ( ele ) {
        var table_name = ele.attr( 'table_name' );

        var hidden_fields = $("#hidden_fields");
        var facility = hidden_fields.find('input[name=facility]').val()
        var formurl = $URL_ROOT + facility + "/core/modal_add/" + table_name;

        var buttons = {};

        $.fn.showModalDialog( formurl, buttons );

        $( document ).off("click", "#modal-add-submit");

        $( document ).on("click", "#modal-add-submit", function ( ) {
            $.fn.modalAddSubmit( );
        } );

        $( document ).off("click", "#modal-add-submit");

        $( document ).on("click", "#modal-add-submit", function ( ) {
            $.fn.modalAddSubmit( );
        } );

        $( ".boolean-field" ).each(
            function( ) {
                $.fn.changeCheckBox( $( this) );
            }
        );
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
                        if ( $( this ).attr( 'type' ) == 'file' ) {
                            form_data.append( $( this ).attr( 'id' ), $( this )[0].files[0] );
                        } else if ( $( this ).attr( 'type' ) == 'checkbox' ) {
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

    $.fn.modal_close = function () {
        $("#dialog").modal( "hide" );
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
        $("#modal_dialog_content").html("");
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

    $.fn.scrollDown = function () {
        for(i=0;i<=jQuery('.multi-row-data').length;i++){
            try{
                var g=jQuery('.multi-row-data')[i];
                g.scrollTop+=1;
                g.scrollTop-=1;
            } catch(e){
            }
        }
    }
} ) ( jQuery );
