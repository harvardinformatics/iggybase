$( document ).ready( function () {
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
    $( ".set_price" ).change(
        function( e ) {
            $.fn.setPrice( e, $( this ) );
        }
    );
} );

( function( $ ) {
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
        var criteria = {'price_item_id': price_item, 'price_type_id': 1};
        var fields = ['price_per_unit'];
        var url = $URL_ROOT + facility + '/core/get_row/price_list/ajax';
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
} ) ( jQuery );
