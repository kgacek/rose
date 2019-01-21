#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta

from my_db import metadata, User, Intention, Prayer, AssociationUR

db = SQLAlchemy(metadata=metadata)


def _get_user(user_id, create=True, status="NEW"):
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user and create:
        user = User(id=user_id, status=status)
        db.session.add(user)
    return user


def update_user(user_id, status="NEW"):
    user = _get_user(user_id)
    user.status = status
    db.session.commit()


def add_user_intentions(user_id, group_list):
    user = _get_user(user_id)
    group_dict = {el["id"]: el['name'] for el in group_list}
    user.intentions = db.session.query(Intention).filter(Intention.id.in_(group_dict.keys())).all()
    db.session.commit()
    return [intention.name for intention in user.intentions]


def get_user_intentions(user_id):
    user = _get_user(user_id)
    intentions = {}
    for intention in user.intentions:
        intentions[intention.name] = []
        for rose in intention.roses:
            if rose.id in [rose.rose_id for rose in user.roses]:
                del intentions[intention.name]
                break
            intentions[intention.name].append(rose.patron.name)
    return intentions


def set_user_roses(data):
    user = _get_user(data['user_id'])
    user.status = "ACTIVE"
    user.roses = []
    for intention in user.intentions:
        for rose in intention.roses:
            if rose.patron.name == data[intention.name]:
                asso = AssociationUR(status="ACTIVE")
                asso.rose = rose
                user.roses.append(asso)
                prayer = Prayer(mystery_id=data[intention.name + '_mystery'])
                prayer.rose = rose
                prayer.user = user
                db.session.add(prayer)
    db.session.commit()
    return True


def subscribe_user(user_id, offset=5):
    expiring_association = db.session.query(AssociationUR).\
                        filter_by(user_id=user_id).\
                        filter(AssociationUR.rose.ends - timedelta(days=offset) < date.today()).all()
    for association in expiring_association:
        association.status = 'SUBSCRIBED'
    db.session.commit()


def unsubscribe_user(user_id):
    user = _get_user(user_id)
    user.roses = []
    user.intentions = []
    user.status = "OBSOLETE"
    db.session.commit()
