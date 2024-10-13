MonthName = new Array(12)
MonthName[0] = "styczeń "
MonthName[1] = "luty "
MonthName[2] = "marzec "
MonthName[3] = "kwiecień "
MonthName[4] = "maj "
MonthName[5] = "czerwiec "
MonthName[6] = "lipiec "
MonthName[7] = "sierpień "
MonthName[8] = "wrzesień "
MonthName[9] = "październik "
MonthName[10] = "listopad "
MonthName[11] = "grudzień "

function setMysteries(intentionSel, rose) {
    var select = document.getElementById(intentionSel.id + "_mystery");
    while (select.firstChild) {
        select.removeChild(select.firstChild);
    }
    if (rose === 'blank'){
        intentionSel.removeAttribute("name");
        select.removeAttribute("name");
        var option = document.createElement('option');
        option.text = "Najpierw wybierz Patrona";
        select.appendChild(option);
    }
    else{
        $.getJSON("https://www.rozamaria.pl/_get_free_mysteries", {
            rose: rose
        }, function (data) {
            intentionSel.name = intentionSel.id;
            select.name = intentionSel.id + "_mystery";
            for (var i = 0; i < data.length; i++) {
                var option = document.createElement('option');
                option.value = data[i];
                option.text = data[i];
                select.appendChild(option);
            }
        });
    }

}

function genTable(data, user_id) {
    var myForm = document.getElementById('myFormDiv');
    while (myForm.firstChild) {
        myForm.removeChild(myForm.firstChild);
    }
    var head = document.createElement("INPUT");
    head.name="user_id";
    head.value=user_id;
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
        select.id=intention;
        select.onchange= function (){setMysteries(this, this.value);};
        var option = document.createElement('option');
        option.text = 'Wybierz swojego Patrona';
        option.value = 'blank';
        select.appendChild(option);
        for (rose in data[intention]) {
            option = document.createElement('option');
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
        option = document.createElement('option');
        option.text = 'Najpierw wybierz Patrona';
        select.appendChild(option);
        container.appendChild(select);
        fieldset.appendChild(container);
        myForm.appendChild(fieldset);
    }
    var btn = document.createElement('BUTTON');
    btn.innerText = "Zapisz mnie";
    btn.className = "myButton";
    myForm.appendChild(btn);

}
function genUlPrayer(data){
    var next = new Date(data['ends'])
    var ul = document.createElement('UL');
    var li = document.createElement('LI');
    if(data['next_status'] === 'TO_APPROVAL')
        var _class= "warning";
    else if (data['next_status'] === 'APPROVED')
        var _class= "approved";
    li.innerText='tajemnica na '+ MonthName[next.getMonth()-1] +':  '+ data['current'];
    li.className= "approved";
    ul.appendChild(li);
    li = document.createElement('LI');
    li.innerText='tajemnica na ' + MonthName[next.getMonth()] + ': ' + data['next'];
    li.className= _class;
    ul.appendChild(li);
    li = document.createElement('LI');
    li.innerText='zmiana nastąpi:  ' + data['ends'];
    li.className= _class;
    ul.appendChild(li);
    return ul;
}

function addPatronPrayer(patron, prayer){
    var prayers = document.getElementById('patronsPrayers');
    var head = document.createElement('h4');
    var p = document.createElement('p');
    head.innerText=patron;
    p.innerText=prayer;
    prayers.appendChild(head);
    prayers.appendChild(p);
}
function addIntentionPrayer(intention, prayer){
    var prayers = document.getElementById('intentionsPrayers');
    var head = document.createElement('h4');
    var p = document.createElement('p');
    head.innerText=intention;
    p.innerText=prayer;
    prayers.appendChild(head);
    prayers.appendChild(p);
}

function user_prayers(user_id) {
    $.getJSON("https://www.rozamaria.pl/_get_users_prayers", {
        user_id: user_id
    }, function (data) {
        var prayers = document.getElementById('patronsPrayers');
        while (prayers.firstChild) {
            prayers.removeChild(prayers.firstChild);
        }
        prayers = document.getElementById('intentionsPrayers');
        while (prayers.firstChild) {
            prayers.removeChild(prayers.firstChild);
        }
        prayers = document.getElementById('prayers');
        while (prayers.firstChild) {
            prayers.removeChild(prayers.firstChild);
        }
        var notification = document.createElement('p')
        if(Object.keys(data).length > 0){
            var ul = document.createElement('UL')
            var approve_needed=false;
            for (var patron in data){
                console.log(patron);
                var li = document.createElement('LI');
                var span = document.createElement('SPAN');
                span.title=data[patron]['intention'];
                span.innerText=patron + '- ' + data[patron]['intention'];
                li.appendChild(span)
                li.appendChild(genUlPrayer(data[patron]));
                ul.appendChild(li);
                if(data[patron]['next_status'] === 'TO_APPROVAL')
                    approve_needed = true;

                if(data[patron]['patron_prayer'] != null)
                    addPatronPrayer(patron, data[patron]['patron_prayer']);
                if(data[patron]['intention_prayer'] != null)
                    addIntentionPrayer(data[patron]['intention'], data[patron]['intention_prayer']);
            }
            prayers.appendChild(ul);
            var btn = document.createElement('BUTTON');

            var current = new Date()
            if (approve_needed)
                btn.innerText = "Potwierdzam uczestnictwo w przyszłym miesiącu";
            else {
                if (current.getDate() > 20){
                btn.innerText = "potwierdziłeś modlitwę w miesiącu " + MonthName[current.getMonth()+1];
                }else{
                btn.innerText = "potwierdziłeś modlitwę w miesiącu " + MonthName[current.getMonth()];
                }
                btn.disabled = true;
            }
            btn.className = "myButton";
            btn.name = 'user_id';
            btn.value = user_id;
            btn.setAttribute("form", "userSub");
            prayers.appendChild(btn)
            notification.innerText='Pomyliłeś się? Wróć do zakładki "moje intencje", wybierz i usuń intencję w której zrobiłeś błąd - Będziesz mógł dodać ją jeszcze raz.'
        }
        else{
        notification.innerText='Prosimy o cierpliwość! Niedługo zostaniesz przydzielony do Róży w Intencji, którą wybrałeś.'
        }
        prayers.appendChild(notification)

    });

}

function clean_forms(){
    var myForm = document.getElementById('myFormDiv');
    while (myForm.firstChild) {
        myForm.removeChild(myForm.firstChild);
    }
}

function already_user(user_id) {
    document.getElementById('choice_buttons').style.display = 'none';
    $.getJSON("https://www.rozamaria.pl/_get_users_intentions", {
        user_id: user_id
    }, function (data) {
        if (!data['active']){
            document.getElementById('statusTitle').innerText = 'Twoje konto nie zostało jeszcze zatwierdzone przez Administratora, cierpliwości!';
        }
        else if (Object.keys(data['intentions']).length > 0) {
            document.getElementById('statusTitle').innerText = 'Wybierz Patrona i aktualnie odmawianą tajemnicę dla każdej róży w której uczestniczysz:';
            genTable(data['intentions'], user_id);
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
        if (['127973684951857', '10205894962648737', '10218775416925342', '2648811858479034', '2364148863618959', '2417174628322246', '2816839405023046', '322686561691681','838937949798703','1948127701931349','1725926644219720'].indexOf(response.authResponse["userID"]) >= 0) { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
            document.getElementById('status').style.display = 'block';
            userList("userList", function (){user_prayers(this.value); clean_forms(); already_user(this.value);})
            already_user(fb_user_id)
        } else {
            updateNavbar('connected');
        }
        user_prayers(fb_user_id)
    }
    else{
    window.location.replace("https://www.rozamaria.pl/");
    }
}
