function selectUser(data, callback) {
    var select = document.createElement('select');
    select.onchange= callback;
    select.name = "user_global_id";
    var option = document.createElement('option');
    option.value = global_id;
    option.text = 'Ja';
    option.selected = 'selected';
    select.appendChild(option);
    for (var user_name in data) {
        option = document.createElement('option');
        option.value = data[user_name];
        option.text = user_name;
        select.appendChild(option);
    }
    return select

}

function userList(elemID, callback){
    $.getJSON("/_get_users",{
    status: 'ALL'
    }, function (data) {
        document.getElementById(elemID).style.display = 'block';
        document.getElementById(elemID).appendChild(selectUser(data, callback));
    });
}

function updateNavbar(status){
    var bar=document.getElementById('navBar')
    while (bar.firstChild) {
        bar.removeChild(bar.firstChild);
    }
    var btn = document.createElement("a");
    btn.className = "navButton"
    btn.href="https://www.rozamaria.pl/"
    btn.innerText="Strona Główna"
    bar.appendChild(btn)

    if (status === "connected" || status === "admin"){
        btn = document.createElement("a");
        btn.className = "navButton"
        btn.href="https://www.rozamaria.pl/intentions"
        btn.innerText="Moje Intencje"
        bar.appendChild(btn)
        btn = document.createElement("a");
        btn.className = "navButton"
        btn.href="https://www.rozamaria.pl/roses"
        btn.innerText="Moje Róże"
        bar.appendChild(btn)


        if (status === "admin"){
            btn = document.createElement("a");
            btn.className = "navButton"
            btn.href="https://www.rozamaria.pl/admin"
            btn.innerText="Panel Administratora"
            bar.appendChild(btn)
        }
        btn = document.createElement("a");
        btn.className = "logButton"
        btn.href="https://www.rozamaria.pl/logout"
        btn.innerText="Wyloguj"
        bar.appendChild(btn)
    }
    else{
        var container = document.createElement("FORM");
        container.method="POST";
        container.style="display: inline-block;";
        container.action="/login";
        var input = document.createElement("INPUT");
        input.type = "text";
        input.name = "login";
        input.className = "navButton";
        input.placeholder="twoj login";
        container.appendChild(input);
        input = document.createElement("INPUT");
        input.type = "text";
        input.name = "password";
        input.className = "navButton";
        input.placeholder="haslo"
        container.appendChild(input);
        btn = document.createElement("input");
        btn.className = "logButton";
        btn.type="submit";
        btn.value="Zaloguj";
        btn.name="action";
        container.appendChild(btn);
        bar.appendChild(container);

    }
}

function loginbutton() {
    FB.getLoginStatus(function (response) {
        LoginCallback(response);
    });
}