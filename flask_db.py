#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
import yaml
import os
import re
import logging
from my_db import metadata, User, Intention, Prayer, AssociationUR, Mystery, Patron, Rose

"""
Module for handling DB related tasks in flask application
"""

with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as f:
    CONFIG = yaml.load(f)

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
db = SQLAlchemy(metadata=metadata)

STAT = {"ACTIVE": 'Aktywny', "SUBSCRIBED": 'Potwierdzony', 'EXPIRED': "Wypisany"}


def _get_user(user_id, create=True, status="NEW"):
    """Gets user db object for given user_id. creates it if don't exist yet.
    :return User object"""
    user = db.session.query(User).filter_by(global_id=user_id).first()
    if not user and create:
        user = User(global_id=user_id, status=status)
        db.session.add(user)
    return user


def get_user_rose_association(user_id):
    """Gets user roses association object including roses from attached account.
    :return list of AssociationUR objects"""
    return db.session.query(AssociationUR).filter_by(user_id=user_id).all() + db.session.query(AssociationUR).filter(AssociationUR.user_id.like('%.' + user_id)).all()


def connect_accounts(user, tmp_user):
    """connects temporary user with true user"""
    user.status = tmp_user.status
    user.intentions = tmp_user.intentions
    for tmp_asso in tmp_user.roses:
        asso = AssociationUR(status="ACTIVE", rose=tmp_asso.rose, user=user)
        new = Prayer(mystery_id=tmp_asso.prayers[-1].mystery_id, ends=tmp_asso.rose.ends)
        asso.prayers.append(new)
        db.session.add(asso)
    db.session.commit()
    unsubscribe_user(user_id=tmp_user.global_id)
    tmp_user.status = 'BLOCKED'
    db.session.commit()


def connect_user_id(user_id, user_psid, username):
    """connects user IDs. invokes when user will start adding intentions via webview in messenger.
    Additionally, fullname is updated."""
    user = _get_user(user_id)
    if user.status != 'BLOCKED':
        if user_psid:
            user.psid = user_psid
        similar_users = db.session.query(User).filter(User.fullname.like(username+'%')).all()
        if similar_users and not [el for el in similar_users if user_id == el.global_id]:
            true_similar_users = [el for el in similar_users if username == el.fullname or re.match(r'{}( - \d\d)'.format(username), el.fullname)]
            if true_similar_users:
                if len(true_similar_users) == 1 and true_similar_users[0].global_id == true_similar_users[0].fullname:
                    connect_accounts(user, true_similar_users[0])
                else:
                    username = '{username} - {number}'.format(username=username, number=str(len(true_similar_users)).zfill(2))
        user.fullname = username
        db.session.commit()
    return user.status


def create_functional_user(user_id):
    """creates new functional account for given user"""
    user = _get_user(user_id)
    if user.status != 'BLOCKED' and user.fullname != user.global_id and "." not in user_id:
        functional_users = db.session.query(User).filter(User.global_id.like('%.' + user_id)).all()
        prefix = str(len(functional_users)+1)
        db.session.add(User(global_id=prefix + "." + user.global_id, fullname="._" + user.fullname + "_." + prefix, status="ACTIVE"))
        db.session.commit()


def create_non_fb_user(non_fb_user):
    """creates new user not connected with Facebook account"""
    if not db.session.query(User).filter_by(fullname=non_fb_user).first():
        db.session.add(User(global_id="." + non_fb_user, fullname="." + non_fb_user + ".", status="ACTIVE"))
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
    if user.status != 'BLOCKED':
        logging.info("Adding new intention for user: " + user.global_id)
        if user.status == 'OBSOLETE':
            user.status = 'VERIFIED'
        intention = db.session.query(Intention).filter(Intention.name == data['intention_name']).first()
        logging.info('Adding: ' + intention.name)
        if intention not in user.intentions:
            user.intentions.append(intention)
        db.session.commit()
    return [intention.name for intention in user.intentions]


def remove_user_intention(data):
    """removes user intention.
    :param data: dict, {user_id: <str>, intention_name: <str>}
    :return list of user intentions
    """
    user = _get_user(data['user_id'])
    logging.info("Removing intention for user: " + user.global_id)
    intention = db.session.query(Intention).filter(Intention.name == data['intention_name']).first()
    logging.warning('Removing: ' + intention.name)
    if intention in user.intentions:
        unsubscribe_user(user_id=user.global_id, intention=intention)
    db.session.commit()
    return [intention.name for intention in user.intentions]


def restore_user(data):
    """restores expired user.
    :param data: dict, {user_id: <str>, rose_name: <str>}
    :return list of user intentions
    """
    association = db.session.query(AssociationUR).join(Rose).join(Patron).filter(AssociationUR.user_id == data['user_id']).filter(Patron.name == data['rose_name']).first()
    if association.status == "EXPIRED":
        logging.warning('restoring: ' + association.user.fullname)
        association.status = "ACTIVE"
        if association.rose.intention_id == "642811842749838":  # Psałterz
            next_id = association.prayers[-1].mystery_id % 170 + (association.prayers[-1].mystery_id // 170) * 20 + 1
        else:
            next_id = association.prayers[-1].mystery_id % 20 + 1
        new = Prayer(mystery_id=next_id, ends=association.rose.ends)
        association.prayers.append(new)
    db.session.commit()


def get_free_rose_name(name, prayers):
    if name in prayers:
        for i in range(1, 100):
            new_name = '{} - {}'.format(name, str(i))
            if new_name not in prayers:
                return new_name
    return name


def get_user_prayers(user_id):
    """Gets user prayers and status
    :param user_id: User.global_id
    :return dict, {<patron name> : {'ends': <cycle end>, 'current':<current mystery>, next:<next mystery>, next_status: <'NOT_ACTIVE','TO_APPROVAL','APPROVED'>, intention: name}..}"""
    prayers = {}
    logging.debug("Getting user prayers information")
    for asso in get_user_rose_association(user_id):
        if asso.status != 'EXPIRED':
            current_mystery = asso.prayers[-1].mystery
            if asso.rose.intention_id == "642811842749838":  # Psałterz
                next_mystery = db.session.query(Mystery).filter_by(id=current_mystery.id % 170 + (current_mystery.id // 170)*20 + 1).first()
            else:
                next_mystery = db.session.query(Mystery).filter_by(id=current_mystery.id % 20 + 1).first()
            if asso.status == 'ACTIVE':
                status = 'TO_APPROVAL' if asso.rose.ends < timedelta(days=CONFIG['reminder_offset']) + date.today() else 'NOT_ACTIVE'
            else:
                status = 'APPROVED'
            rose_name = get_free_rose_name(asso.rose.patron.name, prayers)
            prayers[rose_name] = {'ends': str(asso.rose.ends), 'current': current_mystery.name, 'next': next_mystery.name, 'next_status': status, 'intention': asso.rose.intention.name,
                                  'patron_prayer': asso.rose.patron.prayer, 'intention_prayer': asso.rose.intention.prayer}
    logging.debug(str(prayers))
    return prayers


def get_user_intentions(user_psid, user_id):
    """Gets all user intentions. User can be identified with both app and page scoped ID
    :param user_psid: User psid
    :param user_id: User.global_id
    :return dict, {'intentions': <dict>, 'active': <bool>, 'already_assigned': <dict>}
                    active - true when user.status != 'NEW'
                    intentions - {intention_name: [roses]} only for intentions where user is not yet.
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
            if rose.id in [rose.rose_id for rose in user.roses if rose.status != 'EXPIRED']:
                del intentions[intention.name]
                already_assigned[intention.name] = rose.patron.name
                break
            intentions[intention.name].append(rose.patron.name)
    logging.debug(str(intentions))
    logging.debug(str(already_assigned))
    return {'intentions': intentions, 'active': user.status != 'NEW', 'already_assigned': already_assigned}


def status_sort(elem):
    return elem[-1]


def get_all_status():
    """Gets status of all roses across all intentions
    return dict, {intention:{rose:{user:(status,current mystery}}}"""
    intentions = db.session.query(Intention).all()
    stat = {}
    for intention in intentions:
        stat[intention.name] = {}
        for rose in intention.roses:
            if rose.users:
                stat[intention.name][rose.patron.name] = []
                for asso in rose.users:
                    mystery = asso.prayers[-1].mystery if asso.prayers else '--'
                    stat[intention.name][rose.patron.name].append((asso.user.fullname, STAT.get(asso.status, ''), mystery.name, asso.user.global_id, mystery.id))
                stat[intention.name][rose.patron.name].sort(key=status_sort)
        if not stat[intention.name]:
            del stat[intention.name]
    return stat


def set_user_roses(data):
    """Sets user roses basing on input data.
    :param data: dict, {user_id: <str>. intention_name: <str. assigned rose>, (intention_name)_mystery: mystery_name}"""
    user = _get_user(data['user_id'])
    logging.info('Setting new roses for user - {}'.format(user.global_id))
    mysteries = {k.replace('_mystery', ''): v for (k, v) in data.items() if "_mystery" in k}
    intentions = {k: v for (k, v) in data.items() if "_mystery" not in k and 'user_id' != k and k != 'refresh_url'}
    logging.debug("new roses: {}".format(str(intentions)))
    logging.debug("new mysteries: {}".format(str(mysteries)))
    if mysteries:
        user.status = "ACTIVE"
    for intention, rose in intentions.items():
        rose_obj = db.session.query(Rose).join(Intention).join(Patron).filter(Intention.name == intention).filter(Patron.name == rose).first()
        asso = AssociationUR(status="ACTIVE", rose=rose_obj, user=user)
        mystery = db.session.query(Mystery).filter_by(name=mysteries[intention]).first()
        prayer = Prayer(mystery_id=mystery.id, ends=rose_obj.ends)
        asso.prayers.append(prayer)
        db.session.add(asso)
    db.session.commit()
    return True


def get_current_mysteries(rose):
    """Gets all mysteries currently used in given rose
    :return list of mysteries obj"""
    logging.info("Getting all used mysteries in rose : {}".format(rose.patron.name))
    current_mysteries = []
    for asso in rose.users:
        for prayer in asso.prayers:
            if prayer.ends == rose.ends:
                current_mysteries.append(prayer.mystery)
    return current_mysteries


def get_free_mysteries(rose):
    """Gets all mysteries currently free in given rose
    :return list of free mysteries obj"""
    if not isinstance(rose, Rose):
        rose = db.session.query(Patron).filter_by(name=rose).first().rose
    logging.info("Getting all free mysteries in rose : {}".format(rose.patron.name))
    current_m = get_current_mysteries(rose)
    all_m = db.session.query(Mystery).all()
    if rose.intention_id == "642811842749838":  # Psałterz
        return [el.name for el in all_m if el not in current_m and el.id > 20]
    else:
        return [el.name for el in all_m if el not in current_m and el.id <= 20]


def set_user_verified(data):
    """Sets users status to VERIFIED, basing on input list  of users.
    STATUS CHANGE: after that user status will be'VERIFIED'. used when Admin approves user
    :param data: {user.fullname:..,user2.fullname:.., ...}
    """
    logging.info("Verifying users basing on data: "+str(data))
    users = db.session.query(User).filter(User.fullname.in_(data.keys())).all()
    for user in users:
        logging.debug(user.fullname)
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


def get_users(status):
    """Gets all users with given status.
    :return dict. {username: user id }"""
    if status == 'ALL':
        users = db.session.query(User).filter(User.status != 'BLOCKED').all()
    else:
        users = db.session.query(User).filter(User.status == status).all()
    return {user.fullname: user.global_id for user in users}


def subscribe_user(user_id=None, user_psid=None):
    """Sets  User-Rose relation status to subscibed. should be invoked after user confirmation on messenger.
    STATUS CHANGE: UR asso for roses which ends soon, will be changed from ACTIVE to SUBSCRIBED.
    Affects only roses which have ACTIVE status. EXPIRED asso wont be changed"""
    if user_id:
        user = _get_user(user_id)
    else:
        user = db.session.query(User).filter(User.psid == user_psid).first()
    if user:
        user_asso = get_user_rose_association(user.global_id)
        expiring_association = [asso for asso in user_asso if asso.rose.ends < timedelta(days=CONFIG['reminder_offset']) + date.today()]
        for association in expiring_association:
            if association.status == 'ACTIVE':
                association.status = 'SUBSCRIBED'
        db.session.commit()


def unsubscribe_user(user_id=None, user_psid=None, intention=None):
    """Unsubscribe User from all activities (on user demand).
    STATUS CHANGE: User status will be set to OBSOLETE.
    User Intentions and user roses list will be cleared.
    User Can subscribe again to any intentions he want, bot no confirmation from admins will be needed in this case.
    """
    if user_id:
        user = _get_user(user_id)
    else:
        user = db.session.query(User).filter(User.psid == user_psid).first()
    if user:
        if intention:
            user.intentions.remove(intention)
            asso_u_r = [asso for asso in get_user_rose_association(user.global_id) if asso.rose in intention.roses]
        else:
            user.intentions.clear()
            asso_u_r = get_user_rose_association(user.global_id)

        for asso in asso_u_r:
            asso.prayers.clear()
            db.session.delete(asso)
        if not user.intentions:
            user.status = "OBSOLETE"
        db.session.commit()
    else:
        logging.warning("user have to connect accounts!")
