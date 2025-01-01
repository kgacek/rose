#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user
import flask_db
import yaml
import os
import logging

"""
Flask application
"""

with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as f:
    CONFIG = yaml.load(f)

with open(os.path.join(os.path.dirname(__file__), '.pass_rose_db')) as f:
    PASSWORD = f.readline().strip()

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['sql']['rose']['full_address'].replace('{pass}', PASSWORD)
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flask_db.db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'app.login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return flask_db._get_user(user_id, False)


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else: # login code goes here
        login = request.form.get('login')
        password = request.form.get('password')
        remember = True

        user = flask_db.verify_login_creds(login, password)
        if not user:
            flash('Please check your login details and try again.')
            return redirect(request.form['refresh_url']) # if the user doesn't exist or password is wrong, reload the page
        login_user(user, remember=remember)
        # if the above check passes, then we know the user has the right credentials
        return redirect(url_for('roses'))


@app.route('/')
def index():
    return render_template('index.html', global_id=current_user.global_id)


@app.route('/intentions')
@login_required
def intentions():
    return render_template('intentions.html', global_id=current_user.global_id)

@app.route('/policy')
def policy():
    return render_template('policy.html')


@app.route('/roses')
@login_required
def roses():
    return render_template('roses.html', global_id=current_user.global_id)


@app.route('/admin')
@login_required
def admin():
    status_table = flask_db.get_all_status()
    return render_template('admin.html', status_table=status_table, global_id=current_user.global_id)


@app.route('/_new_users', methods=['GET', 'POST'])
def get_new_users():
    if request.method == 'GET':
        return jsonify(flask_db.get_new_users())
    else:
        data = request.form
        flask_db.set_user_verified(data)
        return redirect(url_for('index'))


@app.route('/_get_users')
def get_users():
    return jsonify(flask_db.get_users(request.args.get('status')))


@app.route('/_process_intention', methods=['GET', 'POST'])
def process_intention():
    data = request.form
    logging.info("processing received intention: " + str(data))
    if data['action'] == 'Dodaj':
        logging.info('adding intention')
        flask_db.add_user_intention(data)
    elif data['action'] == 'Usuń':
        logging.info('removing intention')
        flask_db.remove_user_intention(data)
    return redirect(request.form['refresh_url'])


@app.route('/_remove_users_intention', methods=['GET', 'POST'])
def remove_users_intention():
    data = request.form
    logging.debug(str(data))
    admin = data['admin_id']
    logging.warning('Removing users from intentions by: {}'.format(admin))
    for key, val in data.items():
        if 'admin_id' != key:
            logging.warning("- Removing {} from {}".format(key, val))
            flask_db.remove_user_intention({'user_id': key, 'intention_name': val})
    return redirect(url_for('admin'))


@app.route('/_restore_users', methods=['GET', 'POST'])
def restore_users():
    data = request.form
    logging.debug(str(data))
    admin = data['admin_id']
    logging.warning('Restoring expired users by: {}'.format(admin))
    for key, val in data.items():
        if 'admin_id' != key:
            logging.warning("- Restoring {} in {}".format(key, val))
            flask_db.restore_user({'user_id': key.split('__')[0], 'rose_name': val})
    return redirect(url_for('admin'))


@app.route('/_add_new_user')
def add_new_user():
    status = 'None'
    user_id = request.args.get('user_id')
    user_psid = request.args.get('user_psid')
    if user_id:
        username = bot.get_object(user_id)['name']
        status = flask_db.connect_user_id(user_id, user_psid, username)
    return jsonify({'status': status})


@app.route('/_get_all_intentions')
def get_all_intentions():
    return jsonify(flask_db.get_all_intentions())


@app.route('/_get_free_mysteries')
def get_free_mysteries():
    rose = request.args.get('rose')
    logging.debug("Getting free mysteries for rose: " + str(rose))
    return jsonify(flask_db.get_free_mysteries(rose))


@app.route('/_get_users_prayers', methods=['GET', 'POST'])
def get_users_prayers():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        return jsonify(flask_db.get_user_prayers(user_id))
    else:
        user_id = request.form.get('user_id')
        logging.debug("Subscribing user with id: " + str(user_id))
        flask_db.subscribe_user(user_id)
        return redirect(request.form['refresh_url'])


@app.route('/_get_users_intentions', methods=['GET', 'POST'])
def get_users_intentions():
    if request.method == 'GET':
        user_psid = request.args.get('user_psid')
        user_id = request.args.get('user_id')
        return jsonify(flask_db.get_user_intentions(user_psid, user_id))
    else:
        data = request.form
        flask_db.set_user_roses(data)
        return redirect(request.form['refresh_url'])


@app.route('/_create_functional_user', methods=['GET', 'POST'])
def create_functional_user():
    user_id = request.form.get("user_global_id")
    non_fb_user = request.form.get("non_fb_user")
    if non_fb_user:
        flask_db.create_non_fb_user(non_fb_user)
    if user_id:
        flask_db.create_functional_user(user_id)
    return redirect(request.form['refresh_url'])


@app.route("/webview")
def webview():
    return render_template('webview.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)