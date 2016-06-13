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
        console.log(ele)
    }
} ) ( jQuery );
