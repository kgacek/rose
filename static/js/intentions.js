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
    var id = document.createElement("INPUT");
    id.name="user_id";
    id.value=fb_user_id;
    id.style.display = 'none';
    document.getElementById('newIntention').appendChild(id);
    document.getElementById('statusTitle').innerText = 'Wybierz intencję do której chcesz dołączyć';
    document.getElementById('newIntention').style.display = 'block';
    document.getElementById('newIntentionDiv').appendChild(genSelect(data, 'intention_name'));

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


function genIntentionList(approved, pending) {
    var myTable = document.getElementById('divTable');
    while (myTable.firstChild) {
        myTable.removeChild(myTable.firstChild);
    }
    var row = document.createElement("OL");
    for (var i = 0; i < approved.length; i++) {
        var cell = document.createElement("LI");
        cell.innerText = approved[i];
        console.log(approved[i]);
        row.appendChild(cell);
    }
    for (var i = 0; i < pending.length; i++) {
        cell = document.createElement("LI");
        cell.innerText = pending[i];
        row.appendChild(cell);
    }
    myTable.appendChild(row);
}

function showStatus(user_id) {
    $.getJSON("https://kgacek.pythonanywhere.com/_get_users_intentions", {
        user_id: user_id
    }, function (data) {
        if (!data['active']) {
            document.getElementById('statusTitle').innerText = 'Twoje konto nie zostało jeszcze zatwierdzone przez Administratora, cierpliwości!';
        } else if (Object.keys(data['already_assigned']).length > 0 || Object.keys(data['intentions']).length > 0) {

            document.getElementById('statusTitle').innerText = 'Aktualnie Jesteś zapisany do:';
            document.getElementById('divTable').style.display = 'block';
            genIntentionList(Object.keys(data['already_assigned']), Object.keys(data['intentions']));
        } else {
            document.getElementById('statusTitle').innerText = 'Nie Jesteś zapisany do żadnej Intencji.';
        }

    });
}

function LoginCallback(response) {
    console.log('LoginCallback');
    if (response.status === 'connected') {
        fb_user_id = response.authResponse["userID"];
        if (response.authResponse["userID"] === '2648811858479034') { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
        }
        showStatus(response.authResponse["userID"]);
        fb_user_psid = false; // todo: poprawic
        addIntention()
    }
    else{
    window.location.replace("https://kgacek.pythonanywhere.com/");

    }
}