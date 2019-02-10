#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
import yaml
import os

from my_db import metadata, User, Intention, Prayer, AssociationUR, Mystery

"""
Module for handling DB related tasks in flask application
"""

with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as f:
    CONFIG = yaml.load(f)

db = SQLAlchemy(metadata=metadata)


def _log(msg):
    with open(CONFIG['log']['flask_db'], 'a+') as log:
        log.write(str(msg))


def _get_user(user_id, create=True, status="NEW"):
    """Gets user db object for given user_id. creates it if don't exist yet.
    :return User object"""
    user = db.session.query(User).filter_by(global_id=user_id).first()
    if not user and create:
        user = User(global_id=user_id, status=status)
        db.session.add(user)
    return user


def connect_user_id(user_id, user_psid, username):
    """connects user IDs. invokes when user will start adding intentions via webview in messenger.
    Additionally, fullname is updated."""
    if user_id:
        user = _get_user(user_id)
        if user_psid:
            user.psid = user_psid
        user.fullname = username
        db.session.commit()


def get_all_intentions():
    """Gets all intentions
    :return list of all intentions"""
    return [intention.name for intention in db.session.query(Intention).all()]


def add_user_intention(data):
    """Adds user intention.
    STATUS CHANGE: If user had 'OBSOLETE' status before, after that it gets 'VERIFIED"
    :param data: dict, {user_id: <str>, intention_name: <str>}
    :return list of user intentions
    """
    user = _get_user(data['user_id'])
    if user.status == 'OBSOLETE':
        user.status = 'VERIFIED'
    intention = db.session.query(Intention).filter(Intention.name == data['intention_name']).first()
    print('adding: ' + intention.name)
    if intention not in user.intentions:
        user.intentions.append(intention)
    db.session.commit()
    return [intention.name for intention in user.intentions]


def get_user_prayers(user_id):
    """Gets user prayers and status
    :param user_id: User.global_id
    :return dict, {<patron name> : {'ends': <cycle end>, 'current':<current mystery>, next:<next mystery>, next_status: <'NOT_ACTIVE','TO_APPROVAL','APPROVED'>}..}"""
    user = _get_user(user_id)
    prayers = {}
    for asso in user.roses:
        if asso.status != 'EXPIRED':
            current_mystery = asso.prayers[-1].mystery # ToDo itsw wrong - prayers contains all prayers across all roses!;(
            next_mystery = db.session.query(Mystery).filter_by(id=current_mystery.id % 20 + 1).first()
            if asso.status == 'ACTIVE':
                status = 'TO_APPROVAL' if asso.rose.ends < timedelta(days=CONFIG['reminder_offset']) + date.today() else 'NOT_ACTIVE'
            else:
                status = 'APPROVED'
            prayers[asso.rose.patron.name] = {'ends': str(asso.rose.ends), 'current': current_mystery.name, 'next': next_mystery.name, 'next_status': status}
    _log(prayers)
    return prayers


def get_user_intentions(user_psid, user_id):
    """Gets all user intentions. User can be identified with both app and page scoped ID
    :param user_psid: User psid
    :param user_id: User.global_id
    :return dict, {'intentions': <dict>, 'active': <bool>, 'already_assigned': <dict>}
                    active - true when user.status != 'NEW'
                    intentions - {intention_name: [list of  all rose_ids]} only for intentions where user is not yet.
                    already_assigned - {intention_name: assigned rose}
                    intentions + already_assingned = all intentions"""
    if user_id:
        user = _get_user(user_id)
    else:
        user = db.session.query(User).filter(User.psid == user_psid).first()

    intentions = {}
    already_assigned = {}
    for intention in user.intentions:
        intentions[intention.name] = []
        for rose in intention.roses:
            if rose.id in [rose.rose_id for rose in user.roses]:
                del intentions[intention.name]
                already_assigned[intention.name] = rose.patron.name
                break
            intentions[intention.name].append(rose.patron.name)
    print(str(intentions))
    print(str(already_assigned))
    return {'intentions': intentions, 'active': user.status != 'NEW', 'already_assigned': already_assigned}


def set_user_roses(data):
    """Sets user roses basing on input data.
    :param data: dict, {user_id: <str>. intention_name: <str. assigned rose>, (intention_name)_mystery: mystery_id}"""
    user = _get_user(data['user_id'])
    user.status = "ACTIVE"
    print(str(user.roses))
    for intention in user.intentions:
        if intention.name in data:
            for rose in intention.roses:
                if rose.patron.name == data[intention.name]:
                    asso = AssociationUR(status="ACTIVE", rose=rose, user=user)
                    prayer = Prayer(mystery_id=data[intention.name + '_mystery'], ends=rose.ends)
                    asso.prayers.append(prayer)
                    db.session.add(asso)
    db.session.commit()
    return True


def set_user_verified(data):
    """Sets users status to VERIFIED, basing on input list  of users.
    STATUS CHANGE: after that user status will be'VERIFIED'. used when Admin approves user
    :param data: {user.fullname:..,user2.fullname:.., ...}
    """
    print("data: "+str(data))
    users = db.session.query(User).filter(User.fullname.in_(data.keys())).all()
    for user in users:
        print(user.fullname)
        user.status = 'VERIFIED'
    db.session.commit()


def get_new_users():
    """Gets all users with status == NEW. Admin requests that to get list of users to approve
    :return dict. {username: [list of requested intention to approve]}"""
    users = db.session.query(User).filter(User.status == 'NEW').all()
    user_intentions = {}
    for user in users:
        user_intentions[user.fullname] = [intention.name for intention in user.intentions]
    return user_intentions


def subscribe_user(user_id=None, user_psid=None):
    """Sets  User-Rose relation status to subscibed. should be invoked after user confirmation on messenger.
    STATUS CHANGE: UR asso for roses which ends soon, will be changed from ACTIVE to SUBSCRIBED.
    Affects only roses which have ACTIVE status. EXPIRED asso wont be changed"""
    if user_id:
        user_asso = db.session.query(AssociationUR).filter_by(user_id=user_id).filter_by(status='ACTIVE').all()
    else:
        user_asso = db.session.query(AssociationUR).filter(AssociationUR.user.psid == user_psid).filter_by(status='ACTIVE').all()
    expiring_association = [asso for asso in user_asso if
                            asso.rose.ends < timedelta(days=CONFIG['reminder_offset']) + date.today()]
    for association in expiring_association:
        association.status = 'SUBSCRIBED'
    db.session.commit()


def unsubscribe_user(user_id=None, user_psid=None):
    """Unsubscribe User from all activities (on user demand).
    STATUS CHANGE: User status will be set to OBSOLETE.
    User Intentions and user roses list will be cleared.
    User Can subscribe again to any intentions he want, bot no confirmation from admins will be needed in this case.
    """
    if user_id:
        user = _get_user(user_id)
    else:
        user = db.session.query(User).filter(User.psid == user_psid).first()
    user.intentions.clear()
    for asso in db.session.query(AssociationUR).filter_by(user_id=user_id).all():
        db.session.delete(asso)
    user.status = "OBSOLETE"
    db.session.commit()
