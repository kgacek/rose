window.fbAsyncInit = function () {
        FB.init({
            appId: '1061023747434571',
            xfbml: true,  // parse social plugins on this page
            version: 'v3.2' // use graph api version 2.8

        });
        FB.getLoginStatus(function (response) {
            LoginCallback(response);
        });

    };
    // Load the SDK asynchronously
    (function (d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s);
        js.id = id;
        js.src = "https://connect.facebook.net/pl_PL/sdk.js";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));