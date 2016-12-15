$(document).ready(function(){
    $('#year, #month').change(function() {
        var year_mo = $('#year').val() + '/' + $('#month').val();
        var hidden_fields = $("#hidden_fields");
        var url_prefix = $URL_ROOT + hidden_fields.find('input[name=facility]').val()
            + '/' + hidden_fields.find('input[name=mod]').val() + '/reports/';
        var url = url_prefix + year_mo;
        console.log(url);
        window.location = url;
    });
} );
