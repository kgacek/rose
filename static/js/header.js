function selectUser(data, callback) {
    var select = document.createElement('select');
    select.onchange= callback;
    select.name = "user_global_id";
    var option = document.createElement('option');
    option.value = fb_user_id;
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
    $.getJSON("https://www.rozamaria.pl/_get_users",{
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
    }
    else{
        btn = document.createElement("a");
        btn.className = "logButton"
        btn.href="#"
        btn.onclick= function(){FB.login(function (response) {LoginCallback(response)}); return false;}
        btn.innerText="Zaloguj"
        bar.appendChild(btn)

    }
}

function loginbutton() {
    FB.getLoginStatus(function (response) {
        LoginCallback(response);
    });
}