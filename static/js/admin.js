function showIntentions(intention) {
    var divTables = document.getElementById("intentionsStatus");
    var childTables = divTables.getElementsByTagName("DIV");
    var inputs = divTables.getElementsByTagName("INPUT");
    for (var i=0;i<inputs.length;i++){
        if (inputs[i].type === 'checkbox')
                inputs[i].checked=false;
    }
    for (var i=0;i<childTables.length;i++){
    if (childTables[i].id === intention || intention === 'all')
        childTables[i].style.display="block";
    else
        childTables[i].style.display="none";
    }
}

function genUsersList(data) {
    var div = document.getElementById('divUsersList');
    while (div.firstChild) {
        div.removeChild(div.firstChild);
    }
    var uOl = document.createElement("OL");
    for (var user in data) {
        var li = document.createElement("LI");
        var input = document.createElement("INPUT");
        input.name = user;
        input.value = user;
        input.type = 'checkbox';
        li.appendChild(input);
        var label = document.createElement("LABEL");
        label.innerText = user;
        li.appendChild(label);
        uOl.appendChild(li);

        var iOl = document.createElement("OL");
        for (var i=0;i<data[user].length;i++){
            li = document.createElement("LI");
            li.innerText = data[user][i];
            iOl.appendChild(li);
        }
        uOl.appendChild(iOl);
    }
    div.appendChild(uOl);
}


function LoginCallback(response) {
    console.log('LoginCallback');
    if (response.status === 'connected') {
        fb_user_id = response.authResponse["userID"];
        if (['10218775416925342','2648811858479034', '2364148863618959', '2417174628322246', '2816839405023046', '322686561691681','838937949798703','1948127701931349','1725926644219720'].indexOf(response.authResponse["userID"]) >= 0) { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
            $.getJSON("https://www.rozamaria.pl/_new_users",
                function (data) {
                    if (Object.keys(data).length > 0) {
                        document.getElementById('statusTitle').innerText = 'Aktualnie oczekujący użytkownicy:';
                        document.getElementById('usersList').style.display = 'block';
                        genUsersList(data)
                    } else {
                        document.getElementById('statusTitle').innerText = 'Brak oczekujących użytkowników.';
                        document.getElementById('usersList').style.display = 'none';
                    }
                    document.getElementById('admin_id').value=fb_user_id;
                });
        } else {
            window.location.replace("https://www.rozamaria.pl/");
        }
    }
    else{
    window.location.replace("https://www.rozamaria.pl/");
    }
}
