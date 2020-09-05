$(document).ready(function() {
    $("[name='freeze']").click(function() {
        let id = $(event.target).attr('data-id')

        $.post(window.location.origin + '/students/freeze', {
                url: window.location.origin + '/students/freeze',
                type:"POST",
                student_id: id
            }).done(function(data) {
                if (data["error"] === false) $("#td_name_" + id).attr("bgcolor", data["color"])
                else location.reload()
            })
    });
});