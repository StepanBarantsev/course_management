$(document).ready(function() {
    $("[name='freeze']").click(function() {
        let id = $(event.target).attr('data-id')
         $.ajax({
            url: window.location.origin + '/students/freeze',
            type:"POST",
            data: {"student_id": id},
            success: function(data) {
                $("#td_name_" + id).attr("bgcolor", data["color"])
            }
        });
    });
});