#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymessenger.bot import Bot
import yaml
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import os

from my_db import Base, Intention, Prayer, Rose, Patron, Mystery, User, AssociationUR

"""
Module for handling actions  which should be invoked outside Flask - periodic tasks, DB setup etc.
"""

with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as f:
    CONFIG = yaml.load(f)

bot = Bot(CONFIG['token']['test'])
engine = create_engine(CONFIG['sql']['rose']['full_address'], pool_recycle=280, pool_size=3, max_overflow=0, echo=True)
Session = sessionmaker(bind=engine)


def _log(msg):
    with open(CONFIG['log']['manager'], 'a+') as log:
        log.write(str(msg))


def fill_db():
    _log("fill_db()")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session()
    with open(CONFIG['inputs']['main']) as yaml_file:
        in_data = yaml.load(yaml_file)

    # add intentions
    for el in in_data['intentions']:
        session.add(Intention(id=in_data['intentions'][el], name=el))

    # add roses with patrons
    for intention in in_data['roses']:
        for patron in in_data['roses'][intention]:
            pat = Patron(name=patron)
            rose = Rose(intention_id=intention,
                        started=date.today().replace(day=1),
                        ends=date.today().replace(day=1) + relativedelta(months=1),
                        patron=pat)
            session.add(rose)

    # add patrons
    for el in in_data['patrons']:
        session.add(Patron(name=el))

    for el in in_data['mysteries']:
        session.add(Mystery(name=el))

    session.commit()


class Manager(object):
    def __init__(self):
        self.session = Session()

    def get_not_confirmed_users(self):
        """Gets all user-rose pair with'ACTIVE' status <offset> days before rose.ends
        :return dict {user_id: (intention name, patron name, rose.ends date)}"""
        _log("getting not confirmed users..")
        expiring_roses = self.session.query(Rose).filter(
            Rose.ends < timedelta(days=CONFIG['reminder_offset']) + date.today()).all()
        msg = defaultdict(list)
        for rose in expiring_roses:
            for association in rose.users:
                if association.status == "ACTIVE":
                    msg[association.user.psid].append((rose.intention.name, rose.patron.name, rose.ends))
        _log(msg)
        return msg

    def switch_users(self):
        """Assigns new prayers to users who subscribed, and marks UR asso as EXPIRED for those who don't"""
        # ToDo fix return value or remove it if not necessary
        _log("switching useres to next mysteries..")
        expired_roses = self.session.query(Rose).filter(Rose.ends == date.today()).all()
        msg = {}
        for rose in expired_roses:
            rose.started = rose.ends
            rose.ends = rose.ends + relativedelta(months=1)
            for association in rose.users:
                if association.status == "SUBSCRIBED":  # 1st case - user subscribed for next month
                    association.status = "ACTIVE"
                    new = Prayer(mystery_id=association.prayers[-1].mystery_id % 20 + 1, ends=rose.ends)
                    association.prayers.append(new)
                elif association.status == "ACTIVE":  # 2nd case - user have not subscribed
                    association.status = "EXPIRED"
        self.session.commit()
        _log(msg)
        return msg

    def get_unsubscribed_users(self):
        """Gets users who not subscribed for next month in at least one rose or signed out manually
        :return two tuples with user.global_id for expired and unsubscribed users"""
        _log('getting unsubscribed users..')
        expired_users = set(el.user.psid for el in self.session.query(AssociationUR).filter_by(status="EXPIRED").all())
        unsubscribed_users = [user.psid for user in self.session.query(User).filter_by(status="OBSOLETE").all()]
        _log('expired: {}\n unsubscribed: {}'.format(str(expired_users), str(unsubscribed_users)))
        return tuple(expired_users), tuple(unsubscribed_users)

    def create_new_rose(self, user, intention):
        """Creates new Rose  in <intention>, and adds <user> to it.
        :param user:  User object
        :param intention: Intention object"""
        _log('creating new rose..')
        patron = self.session.query(Patron).filter(Patron.rose == None).first()  # todo handling case when no patrons left
        _log('patron:{}\nintention:{}'.format(patron.name, intention.name))
        rose = Rose(intention_id=intention.id,
                    started=date.today(),
                    ends=date.today() + relativedelta(months=1),
                    patron_id=patron.id)
        asso = AssociationUR(status="ACTIVE")
        asso.rose = rose
        new = Prayer(mystery_id=1, ends=rose.ends)
        asso.prayers.append(new)
        user.roses.append(asso)

    @staticmethod
    def get_free_mystery(rose):
        """Gets first free mystery in given rose
        :return number [0,20] 0 when all mysteries are used"""
        _log("getting first free mystery in rose : {}".format(rose.patron.name))
        current_mysteries = []
        for asso in rose.users:
            for prayer in asso.prayers:
                if prayer.ends == rose.ends:
                    current_mysteries.append(prayer.mystery_id)
        for i in range(1, 21):
            if i not in current_mysteries:
                _log("mystery nr: {}".format(str(i)))
                return i
        return 0

    def attach_new_users_to_roses(self):
        """Attaching new users and users which have more intentions than roses to free mystery. In case of lack of free
        mysteries in current available Roses, new Rose is created."""
        _log('adding new users to roses')
        active_users = self.session.query(User).filter_by(status="ACTIVE").all()
        free_users = self.session.query(User).filter_by(status="VERIFIED").all()
        #  ToDo maybe there is a better way to find people who dont have roses assigned for all intentions
        free_users.extend([user for user in active_users if len(user.roses) < len(user.intentions)])
        self.session.query()
        for user in free_users:
            for intention in user.intentions:
                roses_candidates = self.session.query(Rose).filter_by(intention_id=intention.id).all()
                not_full_roses = [rose for rose in roses_candidates if len(rose.users) < 20]
                if not_full_roses:
                    asso = AssociationUR(status="ACTIVE")
                    asso.rose = not_full_roses[0]
                    new = Prayer(mystery_id=self.get_free_mystery(not_full_roses[0]), ends=not_full_roses[0].ends)
                    asso.prayers.append(new)
                    user.roses.append(asso)
                else:
                    self.create_new_rose(user, intention)
            user.status = "ACTIVE"
            self.session.commit()

    @staticmethod
    def send_reminder(user_psid, roses):
        msg = "Róże w których modlisz się w tym miesiącu:\n"
        for intention, patron, ends in roses:
            msg += "Intencja: {}; Patron: {}; kończy się: {}\n".format(intention, patron, str(ends))
        msg += "Jesli chcesz kontynuować modlitwę w przyszłym miesiacu, napisz/naciśnij 'potwierdzam'.\n "
        msg += "Jeśli nie chcesz więcej brać udziału w różach, napisz/naciśnij 'wypisz mnie'"
        _log('sending msg: {}\nto: {}'.format(msg, user_psid))
        bot.send_text_message(user_psid, msg)

    @staticmethod
    def send_notification_about_expired_users(expired, unsubscribed):
        msg = ''
        for user_psid in expired:
            msg += str(bot.get_user_info(user_psid))
        for user_psid in unsubscribed:
            msg += str(bot.get_user_info(user_psid))
        _log("sending notification about expired users:\n {}".format(msg))  # todo implement real sending


def main():
    manager = Manager()
    users = manager.get_not_confirmed_users()
    for user_psid, roses in users.items():
        manager.send_reminder(user_psid, roses)

    manager.send_notification_about_expired_users(*manager.get_unsubscribed_users())

    manager.switch_users()
    manager.attach_new_users_to_roses()


if __name__ == "__main__":
    main()
