$(document).ready(function() {
    $("#unlock_fields").click(function() {
        $("#lms_email_locked").removeAttr("readonly")
        $("#telegram_id_locked").removeAttr("readonly")
        $("#name_locked").removeAttr("readonly")
        $("#registration_code_locked").removeAttr("readonly")
    });
});