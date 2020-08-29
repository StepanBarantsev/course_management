function showInputFieldIfBooleanChecked(idBoolean, idInput){
    if ($(idBoolean).prop("checked")) {
        $(idInput).show();
    }
    else{
        $(idInput).hide();
    }
}