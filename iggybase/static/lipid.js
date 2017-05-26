$(document).ready(function(){
    $('.normalize').change(function() {
        if ($('input[name=normalize]:checked').val() == 'values') {
            if (!$('.normal_values').is(':visible')) {
                $('.normal_values').toggle();
            }
        } else {
            if ($('.normal_values').is(':visible')) {
                $('.normal_values').toggle();
            }
        }
    });
} );
