function setMysteries(intention, rose) {
    $.getJSON("https://kgacek.pythonanywhere.com/_get_free_mysteries", {
        rose: rose
    }, function (data) {
        var select = document.getElementById(intention + "_mystery");
        while (select.firstChild) {
            select.removeChild(select.firstChild);
        }
        select.name = intention + "_mystery";
        for (var i = 0; i < data.length; i++) {
            var option = document.createElement('option');
            option.value = data[i];
            option.text = data[i];
            select.appendChild(option);
        }
    });

}
function genTable(data) {
    var myForm = document.getElementById('myForm');
    while (myForm.firstChild) {
        myForm.removeChild(myForm.firstChild);
    }
    var head = document.createElement("INPUT");
    head.name="user_id";
    head.value=fb_user_id;
    head.style.display = 'none';
    myForm.appendChild(head)
    head = document.createElement("INPUT");
    head.name="refresh_url";
    head.value="https://kgacek.pythonanywhere.com/roses";
    head.style.display = 'none';
    myForm.appendChild(head)

    for (intention in data) {
        var fieldset = document.createElement("FIELDSET");
        var container = document.createElement("DIV");
        container.className='formContainer';
        head = document.createElement("LEGEND");
        head.innerText = intention;
        fieldset.appendChild(head);
        head = document.createElement("LABEL");
        head.innerText='Patron Róży:';
        head.className='form';
        container.appendChild(head);
        var select = document.createElement('select');
        select.name=intention;
        select.onchange= function (){setMysteries(this.name, this.value);};
        for (rose in data[intention]) {
            var option = document.createElement('option');
            option.value = data[intention][rose];
            option.text = data[intention][rose];
            select.appendChild(option);
        }
        container.appendChild(select);
        fieldset.appendChild(container);
        container = document.createElement("DIV");
        container.className='formContainer';
        head = document.createElement("LABEL");
        head.innerText='Tajemnica:';
        head.className='form';
        container.appendChild(head);
        select = document.createElement('select');
        select.id=intention + "_mystery";
        container.appendChild(select);
        fieldset.appendChild(container);
        myForm.appendChild(fieldset);
        setMysteries(intention, data[intention][0])
    }
    var btn = document.createElement('BUTTON');
    btn.innerText = "Zapisz mnie";
    btn.className = "myButton";
    myForm.appendChild(btn);

}
function genUlPrayer(data){
    var ul = document.createElement('UL');
    var li = document.createElement('LI');
    if(data['next_status'] === 'TO_APPROVAL')
        var _class= "warning";
    else if (data['next_status'] === 'APPROVED')
        var _class= "approved";
    li.innerText='aktualna tajemnica:  '+ data['current'];
    li.className= "approved";
    ul.appendChild(li);
    li = document.createElement('LI');
    li.innerText='następna tajemnica:  ' + data['next'];
    li.className= _class;
    ul.appendChild(li);
    li = document.createElement('LI');
    li.innerText='zmiana nastąpi:  ' + data['ends'];
    li.className= _class;
    ul.appendChild(li);
    return ul;
}

function user_prayers() {
    $.getJSON("https://kgacek.pythonanywhere.com/_get_users_prayers", {
        user_id: fb_user_id
    }, function (data) {
        var prayers = document.getElementById('prayers');
        while (prayers.firstChild) {
            prayers.removeChild(prayers.firstChild);
        }
        if(Object.keys(data).length > 0){
            var ul = document.createElement('UL')
            var approve_needed=false;
            for (var patron in data){
                console.log(patron);
                var li = document.createElement('LI');
                var span = document.createElement('SPAN');
                span.title=data[patron]['intention'];
                span.innerText=patron;
                li.appendChild(span)
                li.appendChild(genUlPrayer(data[patron]));
                ul.appendChild(li);
                if(data[patron]['next_status'] === 'TO_APPROVAL')
                    approve_needed = true;
            }
            prayers.appendChild(ul);
            var btn = document.createElement('BUTTON');
            if (approve_needed)
                btn.innerText = "Potwierdzam uczestnictwo w przyszłym miesiącu";
            else {
                btn.innerText = "Nie możesz jeszcze potwierdzić";
                btn.disabled = true;
            }
            btn.className = "myButton";
            btn.name = 'user_id';
            btn.value = fb_user_id;
            btn.setAttribute("form", "userSub");
            prayers.appendChild(btn)
        }
        else{
        var notification = document.createElement('p')
        notification.className='warning'
        notification.innerText='Nie zostałeś jeszcze przypisany do żadnej Róży. Przydział może nastąpić nawet do 24h po zatwierdzeniu konta przez Administratora, proszę czekać!'
        prayers.appendChild(notification)
        }

    });

}




function already_user() {
    document.getElementById('choice_buttons').style.display = 'none';
    $.getJSON("https://kgacek.pythonanywhere.com/_get_users_intentions", {
        user_id: fb_user_id
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
        }
        else{
            document.getElementById('statusTitle').innerText = 'Nie Jesteś zapisany do żadnej Intencji.';
        }

    });

}

function LoginCallback(response) {
    console.log('LoginCallback');
    if (response.status === 'connected') {
        fb_user_id = response.authResponse["userID"];
        if (['2648811858479034', '2364148863618959', '2417174628322246', '2816839405023046', '322686561691681','838937949798703','1948127701931349','1725926644219720'].indexOf(response.authResponse["userID"]) >= 0) { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
        } else {
            updateNavbar('connected');
        }
        already_user()
        user_prayers()
    }
    else{
    window.location.replace("https://kgacek.pythonanywhere.com/");
    }
}