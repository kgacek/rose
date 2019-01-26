#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python libraries that we need to import for our bot
from flask import Flask, jsonify, request, render_template
from pymessenger.bot import Bot

import flask_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://kgacek:kaszanka12@kgacek.mysql.pythonanywhere-services.com/kgacek$roza?charset=utf8"
flask_db.db.init_app(app)
ACCESS_TOKEN = 'EAAPEZCteQaEsBAKNZBZCT9s9sDPUnsIzYTKGTmUE4ZAGdPiQwi0jBWAnZB2aiDdg6z08ZAGPJrggrwAqr1oJEtKr8J3UphXMK5rlFmUgjZAyOIAsY5B8MrW0bjFw0JjoV64hpOnsPQNQRtI7i92tiqTBf5ZBXlAMGc7KeHiFaZBlUJZChkfcSHSmO1'
ACCESS_TOKEN2 = 'EAAPEZCteQaEsBADHKZAFyVjN4RqXctdGoZAQKVC7Olc7uh3OsGHToFBAm2gpJRZAgZAJaLZAstLeVm7ldL0pcG4drZCAPd8B287ykBVF87axOm3EbUZCjUZCcSyaAfzVOXqZB32l13byySABBVfC12gfw2IGTZCcPz1wZAwB0ug3Ft5dfdDxvKVGZB3U6'
VERIFY_TOKEN = 'TESTINGTOKEN'
APP_ID = '1061023747434571'
bot = Bot(ACCESS_TOKEN)
MODS = ['1594899813943907']


def _log(msg):
    with open('/home/kgacek/fb_bot/my.log', 'a+') as f:
        f.write(msg)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/_set_user_status_to_verified')
def set_user_status_to_verified():
    user_psid = request.args.get('user_psid')
    flask_db.update_user(user_psid, status="VERIFIED")
    return jsonify({'status': 'success'})


@app.route('/_get_users_intentions', methods=['GET', 'POST'])
def get_users_intentions():
    if request.method == 'GET':
        user_psid = request.args.get('user_psid')
        return jsonify(flask_db.get_user_intentions(user_psid))
    else:
        data = request.form
        flask_db.set_user_roses(data)
        return "Message Processed, You can close this window"


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        groups, user_id, user_psid = request.json
        intentions = flask_db.add_user_intentions(user_id, user_psid, groups['data'])
        if intentions:
            msg = "Jesteś zapisany do:\n" + '\n'.join(intentions)
        else:
            msg = "Nie jesteś w żadnej grupie różańcowej, najpierw dołącz do wybranej grupy"
        send_message(user_psid, msg)
        return jsonify(intentions)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/_webhook", methods=['GET', 'POST'])
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


def process_message(recipient_id, msg):
    if "we have new user" in msg:
        return "Witaj w Aplikacji Róż Różańca. Wybierz 'pobierz grupy' z menu aby się zapisać."
    if "zapisz" in msg:
        flask_db.update_user(recipient_id)
        return "Zostaleś zapisany"
    elif "wypisz" in msg:
        flask_db.unsubscribe_user(recipient_id)
        return "Zostaleś wypisany."
    elif "potwierdzam" == msg:
        flask_db.subscribe_user(recipient_id)
        return "Świetnie ;) oczekuj na informację z przydzieloną tajemnicą"

    else:
        return "Nie rozumiem"


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    if recipient_id:
        # sends user the text message provided via input response parameter
        _log("\nsending msg:\n'{0}' \nto '{1}'".format(response, recipient_id))
        bot.send_text_message(recipient_id,  response)
        return "success"
    else:
        return "fail"
