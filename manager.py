#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymessenger.bot import Bot
import yaml
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from my_db import Base, Intention, Prayer, Rose, Patron, Mystery, User, AssociationUR, OFFSET

ACCESS_TOKEN2 = 'EAAPEZCteQaEsBAKNZBZCT9s9sDPUnsIzYTKGTmUE4ZAGdPiQwi0jBWAnZB2aiDdg6z08ZAGPJrggrwAqr1oJEtKr8J3UphXMK5rlFmUgjZAyOIAsY5B8MrW0bjFw0JjoV64hpOnsPQNQRtI7i92tiqTBf5ZBXlAMGc7KeHiFaZBlUJZChkfcSHSmO1'
ACCESS_TOKEN = 'EAAPEZCteQaEsBADHKZAFyVjN4RqXctdGoZAQKVC7Olc7uh3OsGHToFBAm2gpJRZAgZAJaLZAstLeVm7ldL0pcG4drZCAPd8B287ykBVF87axOm3EbUZCjUZCcSyaAfzVOXqZB32l13byySABBVfC12gfw2IGTZCcPz1wZAwB0ug3Ft5dfdDxvKVGZB3U6'
bot = Bot(ACCESS_TOKEN)

engine = create_engine("mysql://kgacek:kaszanka12@kgacek.mysql.pythonanywhere-services.com/kgacek$roza?charset=utf8",
                       pool_recycle=280,
                       pool_size=3,
                       max_overflow=0,
                       echo=True)

Session = sessionmaker(bind=engine)


def fill_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session()
    with open('input_data.yaml') as f:
        in_data = yaml.load(f)

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

    def get_not_confirmed_users(self):  # all user-rose pair with'ACTIVE' status <offset> days before end
        expiring_roses = self.session.query(Rose).filter(Rose.ends < timedelta(days=OFFSET) + date.today()).all()
        msg = defaultdict(list)
        for rose in expiring_roses:
            for association in rose.users:
                if association.status == "ACTIVE":
                    msg[association.user_id].append((rose.intention.name, rose.patron.name, rose.ends))
        return msg

    def switch_users(self):
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
                    self.session.delete(association)
        self.session.commit()
        return msg

    def create_new_rose(self, user, intention):
        patron = self.session.query(Patron).filter(Patron.rose == None).first()
        rose = Rose(intention_id=intention.id,
                    started=date.today(),
                    ends=date.today() + relativedelta(months=1),
                    patron_id=patron.id)
        asso = AssociationUR(status="ACTIVE")
        asso.rose = rose
        new = Prayer(mystery_id=1, ends=rose.ends)
        asso.prayers.append(new)
        user.roses.append(asso)

    def get_unsubscribed_users(self):
        active_users = self.session.query(User).filter_by(status="ACTIVE").all()
        expired_users = [user.id for user in active_users if len(user.roses) < len(user.intentions)]
        unsubscibed_users = [user.id for user in self.session.query(User).filter_by(status="OBSOLETE").all()]
        return expired_users, unsubscibed_users

    def get_free_mystery(self, rose):
        current_mysteries = []
        for asso in rose.users:
            for prayer in asso.prayers:
                if prayer.ends == rose.ends:
                    current_mysteries.append(prayer.mystery_id)
        for i in range(1, 21):
            if i not in current_mysteries:
                return i
        return 0

    def attach_new_users_to_roses(self):
        verified_users = self.session.query(User).filter_by(status="VERIFIED").all()
        for user in verified_users:
            for intention in user.intentions:
                roses_candidates = self.session.query(Rose).filter_by(intention_id=intention.id).all()
                filtered_roses = [rose for rose in roses_candidates if len(rose.users) < 20]
                if filtered_roses:
                    asso = AssociationUR(status="ACTIVE")
                    asso.rose = filtered_roses[0]
                    new = Prayer(mystery_id=self.get_free_mystery(filtered_roses[0]), ends=filtered_roses[0].ends)
                    asso.prayers.append(new)
                    user.roses.append(asso)
                else:
                    self.create_new_rose(user, intention)
            user.status = "ACTIVE"
            self.session.commit()

    def send_reminder(self, user_id, roses):
        msg = "Róże w których modlisz się w tym miesiącu:\n"
        for intention, patron, ends in roses:
            msg += "Intencja: {}; Patron: {}; kończy się: {}\n".format(intention, patron, str(ends))
        msg += "Jesli chcesz kontynuować modlitwę w przyszłym miesiacu, napisz/naciśnij 'potwierdzam'.\n "
        msg += "Jeśli nie chcesz więcej brać udziału w różach, napisz/naciśnij 'wypisz mnie'"

        bot.send_text_message(user_id, msg)

    def send_notification_about_expired_users(self, expired, unsubscribed):
        msg = ''
        for user_id in expired:
            msg += bot.get_user_info(user_id)
        for user_id in unsubscribed:
            msg += bot.get_user_info(user_id)
        print(msg)


def main():
    manager = Manager()
    users = manager.get_not_confirmed_users()
    for user_id, roses in users.items():
        manager.send_reminder(user_id, roses)

    manager.send_notification_about_expired_users(*manager.get_unsubscribed_users())

    manager.switch_users()
    manager.attach_new_users_to_roses()


if __name__ == "__main__":
    main()
