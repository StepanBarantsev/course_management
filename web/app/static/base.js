function showInputFieldIfBooleanChecked(idBoolean, idInput){
    if ($(idBoolean).prop("checked")) {
        $(idInput).show();
    }
    else{
        $(idInput).hide();
    }
}

// Генерация OutLook файла, который потом можно будет открыть
function generate_draft(subject, email, mail){
    var mailHtm =`<p> ${mail} <p>`;
    var emailTo = email;
    var emlCont = 'To: '+ emailTo + '\n';
    emlCont += 'Subject: ' + subject + '\n';
    emlCont += 'X-Unsent: 1'+'\n';
    emlCont += 'Content-Type: text/html; charset=utf-8;'+'\n';
    emlCont += ''+'\n';
    emlCont += "<!DOCTYPE html><html><head></head><body>" + mailHtm + "</body></html>";
    var textFile = null;
    var data = new Blob([emlCont], {type: 'text/plain'});
    if (textFile !== null) {
        window.URL.revokeObjectURL(textFile);
    }
    textFile = window.URL.createObjectURL(data);
    // Для загрузки файла создаем ссылку и кликаем на нее
    // Однако если за раз нужно загрузить несколько писем, ссылку создавать не нужно, нужно просто изменить ее href и возможно название
    if (document.getElementById('fileLink') == undefined){
        var a = document.createElement('a');
        var linkText = document.createTextNode("fileLink");
        a.appendChild(linkText);
        a.id = 'fileLink';
        a.style.visibility = "hidden";
        document.body.appendChild(a);
    }
    document.getElementById('fileLink').href = textFile;
    document.getElementById('fileLink').download = subject + ".eml";
    // В конце кликаем
    document.getElementById('fileLink').click();
}