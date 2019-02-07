var waitForGlobal = function (callback) {
    if (typeof fb_user_psid !== 'undefined') {
        callback();
    } else {
        setTimeout(function () {
            waitForGlobal(callback);
        }, 200);
    }
};

function loginbutton() {
    FB.getLoginStatus(function (response) {
        webviewLoginCallback(response);
    });
}

function webviewLoginCallback(response) {
    console.log('webviewLoginCallback');
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

// ASYNC SDK LOAD/////////////////////////
window.extAsyncInit = function () {
    // the Messenger Extensions JS SDK is done loading
    MessengerExtensions.getContext('1061023747434571',
        function success(thread_context) {
            fb_user_psid = thread_context.psid
            // success
        }
    );
};

(function (d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/messenger.Extensions.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'Messenger'));

window.fbAsyncInit = function () {
    FB.init({
        appId: '1061023747434571',
        cookie: true,  // enable cookies to allow the server to access
                       // the session
        xfbml: true,  // parse social plugins on this page
        version: 'v3.2', // use graph api version 2.8
        status : true
    });
    FB.getLoginStatus(function (response) {
        webviewLoginCallback(response);
    });

};
// Load the SDK asynchronously
(function (d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s);
    js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));