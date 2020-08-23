function showInputFieldIfBooleanChecked(idBoolean, idInput){
    if ($(idBoolean).prop("checked")) {
        $(idInput).show();
    }
    else{
        $(idInput).hide();
    }
}

$(document).ready(function() {
    $("#is_more_then_one_block").change(function() {
        showInputFieldIfBooleanChecked("#is_more_then_one_block", "#number_of_blocks_p")
    });
});