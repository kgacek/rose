function LoginCallback(response) {
    console.log('indexLoginCallback');
    if (response.status === 'connected') {
        updateNavbar('connected');
        if (response.authResponse["userID"] === '2648811858479034') { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
        }
    }
    else{
    updateNavbar('disconnected');
    }
}