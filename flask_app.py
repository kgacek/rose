#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, render_template, redirect, url_for
from pymessenger.bot import Bot

import flask_db
import yaml
import os

"""
Flask application
"""

with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as f:
    CONFIG = yaml.load(f)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['sql']['rose']['full_address']
flask_db.db.init_app(app)
bot = Bot(CONFIG['token']['test'])


def _log(msg):
    with open(CONFIG['log']['flask_app'], 'a+') as f:
        f.write(str(msg))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/_new_users', methods=['GET', 'POST'])
def get_new_users():
    if request.method == 'GET':
        return jsonify(flask_db.get_new_users())
    else:
        data = request.form
        flask_db.set_user_verified(data)
        return redirect(url_for('/'))


@app.route('/_add_intention', methods=['GET', 'POST'])
def add_intention():
    print('adding intention')
    data = request.form
    print(str(data))
    flask_db.add_user_intention(data)
    return redirect(url_for('/login'))


@app.route('/_get_all_intentions')
def get_all_intentions():
    user_psid = request.args.get('user_psid')
    user_id = request.args.get('user_id')
    if user_psid and user_id:
        username = bot.get_user_info(user_id)['name']
        flask_db.connect_user_id(user_id, user_psid, username)
    return jsonify(flask_db.get_all_intentions())


@app.route('/_get_users_intentions', methods=['GET', 'POST'])
def get_users_intentions():
    if request.method == 'GET':
        user_psid = request.args.get('user_psid')
        user_id = request.args.get('user_id')
        return jsonify(flask_db.get_user_intentions(user_psid, user_id))
    else:
        data = request.form
        flask_db.set_user_roses(data)
        return "Message Processed, You can close this window"


@app.route("/login")
def login():
    return render_template('login.html')


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
                _log(message)
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
    if token_sent == CONFIG['token']['verify_webhook']:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


def process_message(recipient_id, msg):
    if "we have new user" in msg:
        return "Witaj w Aplikacji Róż Różańca. Wybierz 'Uruchom Aplikację' aby się zapisać."
    elif "wypisz" in msg:
        flask_db.unsubscribe_user(recipient_id)
        return "Zostaleś wypisany."
    elif "zapisz" in msg:  # ToDo remove after review
        return "Zostaleś zapisany."
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
