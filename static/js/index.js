function LoginCallback(response) {
    console.log('indexLoginCallback');
    if (response.status === 'connected') {
        updateNavbar('connected');
        if (['2648811858479034', '2364148863618959', '2417174628322246', '2816839405023046', '322686561691681', '838937949798703','1948127701931349','1725926644219720'].indexOf(response.authResponse["userID"]) >= 0) { //TODO: trzeba dodac liste adminow
            updateNavbar('admin');
        }
    }
    else{
    updateNavbar('disconnected');
    }
}