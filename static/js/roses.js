function genTable(data) {
    var myTable = document.getElementById('myTable');
    while (myTable.firstChild) {
        myTable.removeChild(myTable.firstChild);
    }
    var row = document.createElement("TR");
    var tbody = document.createElement("TBODY");
    var thead = document.createElement("THEAD");
    var cell = document.createElement("TH");
    cell.innerText = "patron";
    row.appendChild(cell);
    cell = document.createElement("INPUT");
    cell.name="user_id";
    cell.value=fb_user_id;
    cell.style.display = 'none';
    row.appendChild(cell);
    cell = document.createElement("TH");
    cell.innerText = "nr taj.";
    row.appendChild(cell);
    thead.appendChild(row);
    for (intention in data) {
        row = document.createElement("TR");
        cell = document.createElement("TD");
        cell.innerText = intention;
        cell.colSpan = "2";
        row.appendChild(cell);
        tbody.appendChild(row);
        row = document.createElement("TR")

        var select = document.createElement('select');
        select.name=intention;
        select.style.width= '100%';
        for (rose in data[intention]) {
            var option = document.createElement('option');
            option.value = data[intention][rose];
            option.text = data[intention][rose];
            select.appendChild(option);
        }
        cell = document.createElement("TD");
        cell.appendChild(select);
        row.appendChild(cell);
        cell = document.createElement("TD");
        var x = document.createElement("INPUT");
        x.setAttribute("type", "number");
        x.setAttribute("maxlength", '2');
        x.style.width = "3em";
        x.min='1';
        x.max='20';
        x.required = true;
        x.name=intention+"_mystery";
        cell.appendChild(x);
        row.appendChild(cell);
        tbody.appendChild(row);

    }
    myTable.appendChild(thead);
    myTable.appendChild(tbody);
}

function already_user() {
    document.getElementById('choice_buttons').style.display = 'none';
    $.getJSON("https://kgacek.pythonanywhere.com/_get_users_intentions", {
        user_psid: fb_user_psid
    }, function (data) {
        if (!data['active']){
            document.getElementById('statusTitle').innerText = 'Twoje konto nie zostało jeszcze zatwierdzone przez Administratora, cierpliwości!';
        }
        else if (Object.keys(data['intentions']).length > 0) {
            document.getElementById('statusTitle').innerText = 'Wybierz Patrona i aktualnie odmawianą tajemnicę dla każdej róży w której uczestniczysz:';
            document.getElementById('myForm').style.display = 'block';
            genTable(data['intentions']);
        }
        else if (Object.keys(data['already_assigned']).length > 0) {
            document.getElementById('statusTitle').innerText = 'Masz już przypisane tajemnice dla wszystkich Intencji w których się modlisz.';
            setTimeout(function () {
                MessengerExtensions.requestCloseBrowser();
            }, 8000);

        }
        else{
            document.getElementById('statusTitle').innerText = 'Nie Jesteś zapisany do żadnej Intencji.';
            setTimeout(function () {
                MessengerExtensions.requestCloseBrowser();
            }, 3000);
        }

    });

}

function LoginCallback(response) {
    console.log('LoginCallback');
    if (response.status === 'connected') {
        fb_user_id = response.authResponse["userID"];
        if (response.authResponse["userID"] === '2648811858479034') { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
            document.getElementById('statusTitle').innerText = 'Logowanie się powiodło Adminie, twoje ID to ' + fb_user_id;
        } else {
            updateNavbar('connected');
            document.getElementById('statusTitle').innerText = 'Logowanie się powiodło, twoje ID to ' + fb_user_id;
        }
    }
    else{
    window.location.replace("https://kgacek.pythonanywhere.com/");
    }
}