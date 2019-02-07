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