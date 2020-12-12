function generateNewUrlForStudentsSearch() {
    let url = window.location.href
    let val = $('.basicAutoComplete').val()
    let data = {"student_search": val}
    url = url.replace(/student_search=.+?&?/, "").replace("#!", "") + "&" + jQuery.param(data)
    window.location.href = url
}

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


$(document).ready(function() {
    $("[name='finish']").click(function() {
        let id = $(event.target).attr('data-id')

        $.post(window.location.origin + '/students/finish', {
                url: window.location.origin + '/students/finish',
                type:"POST",
                student_id: id
            }).done(function(data) {
                if (data["error"] === false) $("#td_name_" + id).attr("bgcolor", data["color"])
                else location.reload()
            })
    });
});

$(document).ready(function() {
    $("[name='drop_course']").click(function() {
        let id = $(event.target).attr('data-id')

        $.post(window.location.origin + '/students/drop', {
                url: window.location.origin + '/students/drop',
                type:"POST",
                student_id: id
            }).done(function(data) {
                if (data["error"] === false) $("#td_name_" + id).attr("bgcolor", data["color"])
                else location.reload()
            })
    });
});

$('.basicAutoComplete').autoComplete({
    delay: 0,
});


$('.basicAutoComplete').keypress(function(event){
  if(event.keyCode == 13){
    generateNewUrlForStudentsSearch()
  }
});

$('#search_student').click(function(event){
  generateNewUrlForStudentsSearch()
});
