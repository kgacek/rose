from my_db import metadata, User, Intention, Prayer
from flask_sqlalchemy import SQLAlchemy

from datetime import date
from dateutil.relativedelta import relativedelta

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
            intentions[intention.name].append(rose.patron.name)
    return intentions


def set_user_roses(data):
    user = _get_user(data['user_id'])
    user.status = "ACTIVE"
    user.roses = []
    for intention in user.intentions:
        for rose in intention.roses:
            if rose.patron.name == data[intention.name]:
                user.roses.append(rose)
                prayer = Prayer(mystery_id=data[intention.name + 'taj'], started=date.today().replace(day=1))
                prayer.ends = prayer.started + relativedelta(months=1)
                prayer.rose = rose
                prayer.user = user
                db.session.add(prayer)
    db.session.commit()
    return True


def subscribe_user(user_id):
    update_user(user_id, status="SUBSCRIBED")


def unsubscribe_user(user_id):
    user = _get_user(user_id)
    for prayer in user.prayers:
        prayer.rose = None
    user.roses = []
    user.intentions = []
    user.status = "OBSOLETE"
    db.session.commit()
