# Python libraries that we need to import for our bot
from flask import Flask, request, render_template
from pymessenger.bot import Bot

import my_db
import manager

app = Flask(__name__)
ACCESS_TOKEN = 'EAAPEZCteQaEsBADHKZAFyVjN4RqXctdGoZAQKVC7Olc7uh3OsGHToFBAm2gpJRZAgZAJaLZAstLeVm7ldL0pcG4drZCAPd8B287ykBVF87axOm3EbUZCjUZCcSyaAfzVOXqZB32l13byySABBVfC12gfw2IGTZCcPz1wZAwB0ug3Ft5dfdDxvKVGZB3U6'
VERIFY_TOKEN = 'TESTINGTOKEN'
APP_ID = '1061023747434571'
bot = Bot(ACCESS_TOKEN)
MODS = ['1594899813943907']


def _log(msg):
    with open('/home/kgacek/fb_bot/my.log', 'a+') as f:
        f.write(msg)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        groups, user_psid = request.json
        intentions = my_db.add_user_intentions(user_psid, groups['data'])
        if intentions:
            msg = "Jesteś zapisany do:\n" + '\n'.join(intentions)
        else:
            msg = "Nie jesteś w żadnej grupie różańcowej, najpierw dołącz do wybranej grupy"
        send_message(user_psid, msg)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = process_message(recipient_id, message['message'].get('text'))
                        send_message(recipient_id, response_sent_text)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'



# chooses a random message to send to the user
def process_message(recipient_id, msg):
    if "zapisz" in msg:
        my_db.update_user(recipient_id)
        return "Zostaleś zapisany"
    elif "wypisz" in msg:
        my_db.unsubscribe_user(recipient_id)
        return "Zostaleś wypisany."
    elif "potwierdzam" == msg:
        my_db.subscribe_user(recipient_id)
        return "Świetnie ;) oczekuj na informację z przydzieloną tajemnicą"

    else:
        return "Nie rozumiem"


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    _log("\nsending msg:\n'{0}' \nto '{1}'".format(response, recipient_id))
    bot.send_text_message(recipient_id,  response)
    return "success"
