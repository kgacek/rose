#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta

from my_db import metadata, User, Intention, Prayer, AssociationUR, OFFSET

db = SQLAlchemy(metadata=metadata)


def _get_user(user_psid, create=True, status="NEW"):
    user = db.session.query(User).filter_by(psid=user_psid).first()
    if not user and create:
        user = User(psid=user_psid, status=status)
        db.session.add(user)
    return user


def update_user(user_psid, status="NEW"):
    user = _get_user(user_psid)
    if status == "VERIFIED" and user.status != "NEW":
        return False
    else:
        user.status = status
        db.session.commit()
        return True


def connect_user_id(user_id, user_psid, username):
    if user_psid:
        user = _get_user(user_psid)
        if user.global_id != user_id:
            user.global_id = user_id
            user.fullname = username
            db.session.commit()


def get_all_intentions():
    return [intention.name for intention in db.session.query(Intention).all()]


def add_user_intention(data):
    user = _get_user(data['user_psid'])
    if user.status == 'OBSOLETE':
        user.status = 'VERIFIED'
    intention = db.session.query(Intention).filter(Intention.name == data['intention_name']).first()
    print('adding: ' + intention.name)
    if intention not in user.intentions:
        user.intentions.append(intention)
    db.session.commit()
    return [intention.name for intention in user.intentions]


def add_user_intentions(user_id, user_psid, group_list):
    group_dict = {el["id"]: el['name'] for el in group_list}
    intentions = db.session.query(Intention).filter(Intention.id.in_(group_dict.keys())).all()
    if user_psid:
        user = _get_user(user_psid)
        user.intentions = intentions
        user.global_id = user_id
        db.session.commit()
    return [intention.name for intention in intentions]


def get_user_intentions(user_psid, user_id):
    if user_psid:
        user = _get_user(user_psid)
    else:
        user = User(psid='uid'+user_id, global_id=user_id, status='NEW')
        _user = db.session.query(User).filter(User.global_id == '').first()

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
    user = _get_user(data['user_psid'])
    user.status = "ACTIVE"
    print(str(user.roses))
    for intention in user.intentions:
        if intention.name in data:
            for rose in intention.roses:
                if rose.patron.name == data[intention.name]:
                    asso = AssociationUR(status="ACTIVE")
                    asso.rose = rose
                    user.roses.append(asso)
                    prayer = Prayer(mystery_id=data[intention.name + '_mystery'], ends=rose.ends)
                    prayer.association = asso
                    db.session.add(prayer)
    db.session.commit()
    return True


def set_user_verified(data):
    print("data: "+str(data))
    users = db.session.query(User).filter(User.fullname.in_(data.keys())).all()
    for user in users:
        print(user.fullname)
        user.status = 'VERIFIED'
    db.session.commit()


def get_new_users():
    users = db.session.query(User).filter(User.status == 'NEW').all()
    user_intentions = {}
    for user in users:
        user_intentions[user.fullname] = [intention.name for intention in user.intentions]
    return user_intentions


def subscribe_user(user_psid):
    user_asso = db.session.query(AssociationUR).filter_by(user_psid=user_psid).all()
    expiring_association = [asso for asso in user_asso if asso.rose.ends < timedelta(days=OFFSET) + date.today()]
    for association in expiring_association:
        association.status = 'SUBSCRIBED'
    db.session.commit()


def unsubscribe_user(user_psid):
    user = _get_user(user_psid)
    user.intentions.clear()
    for asso in db.session.query(AssociationUR).filter_by(user_psid=user_psid).all():
        db.session.delete(asso)
    user.status = "OBSOLETE"
    db.session.commit()
