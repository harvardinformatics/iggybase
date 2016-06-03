$( document ).ready( function () {
    $( ".charge-method-code" ).blur(
        function( ) {
            $.fn.checkCodeFormat( $( this ) );
        }
    );
} );

( function( $ ) {
    $.fn.checkCodeFormat = function( ele ) {
        var code_type_ctrl;
        var code_type;

        if ( ele.closest( 'tr' ).find( '.charge-method-type' ).length ) {
            code_type_ctrl = ele.closest( 'tr' ).find( '.charge-method-type' );
        } else {
            code_type_ctrl = ele.closest( 'tr' ).parent().find( '.charge-method-type' );
        }

        if ( $( code_type_ctrl ).prop( 'type' ) == 'select-one' ) {
            code_type = $( '#' + code_type_ctrl.attr( 'id' ) + ' option:selected' ).text();
        } else {
            code_type = code_type_ctrl.val();
        }

        if ( code_type == 'Harvard Code' ) {
            var code_match = ele.val().match( /^(\d{3})(.)(\d{5})(.)(\d{4})(.)(\d{6})(.)(\d{6})(.)(\d{4})(.)(\d{5})$/ );
            if ( !code_match ) {
                ele.select();
                alert( 'Code is not the correct format.\n\n###.#####.####.######.######.####.#####' );
            } else {
                code = code_match[ 1 ] + "." + code_match[ 3 ] + "." + code_match[ 5 ] + "." + code_match[ 7 ] + "." + code_match[ 9 ] + "." + code_match[ 11 ] + "." + code_match[ 13 ];
                spinal_code = code_match[ 1 ] + "-" + code_match[ 3 ] + "-" + code_match[ 5 ] + "-" + code_match[ 7 ] + "-" + code_match[ 9 ] + "-" + code_match[ 11 ] + "-" + code_match[ 13 ];
                ele.val( code );

                var hidden_fields = $("#hidden_fields");
                var facility = hidden_fields.find('input[name=facility]').val()
                var url = $URL_ROOT + facility + "/core/check_harvard_code";

                $.ajax( {
                    url: url,
                    data: { spinal_code: spinal_code }
                    success: function ( resp ) {
                        if ( resp != 'found' ) {
                            alert('code was not verified in Spinal, it may still be valid.\n\nPlease confirm the code.');
                        }
                    }
                } );
            }
        }
    }
} ) ( jQuery );