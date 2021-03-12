    $("#btn_xls_with_parameters").click(function(e) {
        prepare_xls(e, 'xls_with_parameters');
        $("#hdn_with_grp").val('');
        $("#hdn_with_attributions").val('');
    });
    $("#btn_produce_xls_detailled_attributions").click(function (e) {
        prepare_xls(e, 'xls_attributions');
    });
    $("#btn_produce_xls_educational_specifications").click(function (e) {
        prepare_xls(e, 'xls_educational_specifications');
    });
    $("#btn_produce_xls_one_pgm_per_line").click(function (e) {
        prepare_xls(e, 'xls_one_pgm_per_line');
    });
