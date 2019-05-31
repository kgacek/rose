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

function selectIntention(data, user_id) {
    var id = document.createElement("INPUT");
    id.id="user_id"
    id.name="user_id";
    id.value=user_id;
    id.style.display = 'none';
    document.getElementById('newIntention').appendChild(id);
    document.getElementById('newIntentionDiv').appendChild(genSelect(data, 'intention_name'));

}

function IntentionForm(user_id){
    $.getJSON("https://www.rozamaria.pl/_get_all_intentions",
    function (data) {
        selectIntention(data, user_id);
    });
}

function genIntentionList(approved, pending) {
    var myTable = document.getElementById('divTable');
    while (myTable.firstChild) {
        myTable.removeChild(myTable.firstChild);
    }
    var head = document.createElement("P");
    head.innerText='Intencje do których jesteś zapisany:';
    myTable.appendChild(head);
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
    $.getJSON("https://www.rozamaria.pl/_get_users_intentions", {
        user_id: user_id
    }, function (data) {
        var status = document.getElementById('statusTitle')
        if (Object.keys(data['already_assigned']).length > 0 || Object.keys(data['intentions']).length > 0) {
            if (!data['active']) {
                status.innerText = 'Twoje konto nie zostało jeszcze zatwierdzone przez Administratora, twoje intencje nie są jeszcze aktywne! proszę czekać';
                status.className = 'warning'
            }
            else{
                status.className = 'approved'
                status.innerText = 'Twoje konto jest Aktywne! Po zapisaniu do intencji sprawdź zakładkę "Moje Róże"';
            }
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
        showStatus(fb_user_id);
        if (['127973684951857', '10205894962648737', '10218775416925342', '2648811858479034', '2364148863618959', '2417174628322246', '2816839405023046', '322686561691681', '838937949798703','1948127701931349','1725926644219720'].indexOf(response.authResponse["userID"]) >= 0) { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
            userList("userList", function (){document.getElementById('user_id').value=this.value; showStatus(this.value); })
        }else {
            updateNavbar('connected');
        }
        IntentionForm(fb_user_id)
    }
    else{
    window.location.replace("https://www.rozamaria.pl/");

    }
}
