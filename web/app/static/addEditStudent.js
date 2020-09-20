$(document).ready(function() {
    $("#unlock_fields").click(function() {
        if ($("#unlock_fields").attr("data-flag") == "True") {
            $("#unlock_fields").attr("data-flag", "False")
            $("#unlock_fields").text("Запретить менять поля")
            $("#lms_email_locked").removeAttr("readonly")
            $("#telegram_id_locked").removeAttr("readonly")
            $("#name_locked").removeAttr("readonly")
            $("#registration_code_locked").removeAttr("readonly")
        }
        else {
            $("#unlock_fields").attr("data-flag", "True")
            $("#unlock_fields").text("Разрешить менять заблокированные поля")
            $("#lms_email_locked").prop("readonly",true)
            $("#telegram_id_locked").prop("readonly",true)
            $("#name_locked").prop("readonly",true)
            $("#registration_code_locked").prop("readonly",true)
        }
    });
});