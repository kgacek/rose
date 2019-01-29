
var waitForGlobal = function (callback) {
    if (typeof fb_user_psid !== 'undefined') {
        callback();
    } else {
        setTimeout(function () {
            waitForGlobal(callback);
        }, 200);
    }
};

function genSelect(data, select_name) {
    var select = document.createElement('select');
    select.name=select_name;
    select.style.width= '100%';
    for (var i=0; i<data.length; i++) {
        var option = document.createElement('option');
        option.value = data[i];
        option.text = data[i];
        select.appendChild(option);
    }
    return select
}

function selectIntention(data) {
    var psid = document.createElement("INPUT");
    psid.name="user_psid";
    psid.value=fb_user_psid;
    psid.style.display = 'none';
    document.getElementById('newIntention').appendChild(psid);
    document.getElementById('statusTitle').innerText = 'Wybierz intencję do której chcesz dołączyć';
    document.getElementById('newIntention').style.display = 'block';
    document.getElementById('newIntentionDiv').appendChild(genSelect(data, 'intention_name'));

}

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
    cell.name="user_psid";
    cell.value=fb_user_psid;
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
        } else {
            document.getElementById('statusTitle').innerText = 'Nie Jesteś zapisany do żadnej Intencji lub już wcześniej skonfigurowałeś swoje konto!';
            setTimeout(function () {
                MessengerExtensions.requestCloseBrowser();
            }, 3000);
        }

    });

}

function addIntention() {
    console.log('addIntention');
    document.getElementById('choice_buttons').style.display = 'none';
    $.getJSON("https://kgacek.pythonanywhere.com/_get_all_intentions", {
        user_psid: fb_user_psid,
        user_id: fb_user_id,
    }, function (data) {
        selectIntention(data);
    });
    document.getElementById('statusTitle').innerText = 'Wybierz intencję do której chcesz dołączyć';
    document.getElementById('newIntention').style.display = 'block';

}

function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    if (response.status === 'connected') {
        waitForGlobal(function () {
            fb_user_id = response.authResponse["userID"];
            document.getElementById('statusTitle').innerText = 'Logowanie się powiodło';
            document.getElementById('loginBtn').style.display = 'none';
            document.getElementById('choice_buttons').style.display = 'block';
        });
    } else {
        document.getElementById('statusTitle').innerText = 'Zaloguj się do aplikacji, aby wczytać intencje do których należysz i ustawić aktualną tajemnicę.';
        document.getElementById('loginBtn').style.display = 'block';
    }
}

function loginbutton() {
    FB.getLoginStatus(function (response) {
        statusChangeCallback(response);
    });
}
function loginbutton2() {
    FB.getLoginStatus(function (response) {
        statusChangeCallback2(response);
    });
}
function genIntentionList(data) {
    var myTable = document.getElementById('divTable');
    while (myTable.firstChild) {
        myTable.removeChild(myTable.firstChild);
    }
    var row = document.createElement("OL");
    for (var i = 0; i < data.length; i++) {
        var cell = document.createElement("LI");
        cell.innerText = data[i];
        row.appendChild(cell);
    }
    myTable.appendChild(row);
}

function statusChangeCallback2(response) {
    console.log('statusChangeCallback');
    if (response.status === 'connected') {

        FB.api("/" + response.authResponse["userID"] + "/groups", {access_token: response.authResponse["accessToken"]}, function (response2) {
            if (response2 && !response2.error)
                var data_json = JSON.stringify([response2, response.authResponse["userID"], ''], null, '\t');
            console.log(data_json);
            $.ajax({
                url: "https://kgacek.pythonanywhere.com/login",
                method: "post",
                contentType: 'application/json;charset=UTF-8',
                data: data_json
            }).done(function (data) {
                if (data.length > 0) {
                    document.getElementById('tableTitle').innerText = 'Jesteś zapisany do następujących Intencji:';
                    document.getElementById('divTable').style.display = 'block';
                    genIntentionList(data);
                } else {
                    document.getElementById('tableTitle').innerText = 'Nie Jesteś zapisany do żadnej Intencji!';
                }
            });
        });

    } else {
        document.getElementById('tableTitle').innerText = 'Zaloguj się do aplikacji aby zobaczyć do jakich Intencji jesteś zapisany.';
        document.getElementById('divTable').style.display = 'none';
    }
}
