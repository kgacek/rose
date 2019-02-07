function updateNavbar(status){
    var bar=document.getElementById('navBar')
    while (bar.firstChild) {
        bar.removeChild(bar.firstChild);
    }
    var btn = document.createElement("a");
    btn.className = "navButton"
    btn.href="https://kgacek.pythonanywhere.com/"
    btn.innerText="Strona Główna"
    bar.appendChild(btn)

    if (status === "connected" || status === "admin"){
        btn = document.createElement("a");
        btn.className = "navButton"
        btn.href="https://kgacek.pythonanywhere.com/roses"
        btn.innerText="Moje Róże"
        bar.appendChild(btn)
        btn = document.createElement("a");
        btn.className = "navButton"
        btn.href="https://kgacek.pythonanywhere.com/intentions"
        btn.innerText="Moje Intencje"
        bar.appendChild(btn)

    }
    if (status === "admin"){
        btn = document.createElement("a");
        btn.className = "navButton"
        btn.href="https://kgacek.pythonanywhere.com/admin"
        btn.innerText="Panel Administratora"
        bar.appendChild(btn)
    }
}

function loginbutton() {
    FB.getLoginStatus(function (response) {
        LoginCallback(response);
    });
}