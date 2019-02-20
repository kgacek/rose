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
        if (['2648811858479034', '2364148863618959', '2417174628322246', '2816839405023046', '322686561691681','838937949798703','1948127701931349','1725926644219720'].indexOf(response.authResponse["userID"]) >= 0) { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
            $.getJSON("https://kgacek.pythonanywhere.com/_new_users",
                function (data) {
                    if (Object.keys(data).length > 0) {
                        document.getElementById('statusTitle').innerText = 'Aktualnie oczekujący użytkownicy:';
                        document.getElementById('usersList').style.display = 'block';
                        genUsersList(data)
                    } else {
                        document.getElementById('statusTitle').innerText = 'Brak oczekujących użytkowników.';
                        document.getElementById('usersList').style.display = 'none';

                    }
                });
        } else {
            window.location.replace("https://kgacek.pythonanywhere.com/");
        }
    }
    else{
    window.location.replace("https://kgacek.pythonanywhere.com/");
    }
}