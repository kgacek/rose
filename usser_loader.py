from collections import defaultdict
import re
import manager
from my_db import  Intention, Prayer, Rose, Patron, Mystery, User, AssociationUR

all_roses = set()
for el in input['roses'].values():
    all_roses.update(el)


def read_user_list():
    all_users = defaultdict(list)
    with open('all_users.csv') as f:
        for line in f:
            list_line = line.strip('\r\n').split(',')
            if list_line:
                if not list_line[1] and list_line[0]:
                    key = list_line[0]
                elif list_line[1] and list_line[0]:
                    username, mystery = list_line
                    macz = re.match(r'^\d+.?(.*)', username)
                    if macz:
                        username = macz.group(1).strip()
                    macz2 = re.search(r'(.*)\(', username)
                    if macz2:
                        username = macz2.group(1).strip()
                    all_users[username.strip(',. ')].append((key, mystery.strip('"- ')))
    return all_users


def get_wrong_users(db, all_users):

    wrong = defaultdict(list)
    for user, mysteries in all_users.items():
        db_user = db.session.query(User).filter_by(fullname=user).first()
        if db_user:
            for patron, mystery in mysteries:
                intention = db.session.query(Intention).join(Rose).join(Patron).filter(Patron.name == patron).first()
                rose_obj = db.session.query(Rose).join(Patron).filter(Patron.name == patron).first()
                mystery = db.session.query(Mystery).filter_by(name=mystery).first()
                if rose_obj and intention and mystery:
                    match = [rose for rose in db_user.roses if rose.rose.patron == patron]
                    if not match:
                        wrong[user].append(patron)
                    elif match[0].prayers[-1].mystery.name == mystery:
                        wrong[user].append((patron, mystery))
                else:
                    wrong[user].append((patron, mystery))
    return wrong


def add_new_users(db, all_users):
    for user, mysteries in all_users.items():
        add_new_user(db, user, mysteries)


def add_new_user(db, user, mysteries):
    db_user = db.session.query(User).filter_by(fullname=user).first()
    if not db_user:
        new_user = User(global_id=user, fullname=user, status='ACTIVE')
        for patron, mystery in mysteries:
            intention = db.session.query(Intention).join(Rose).join(Patron).filter(Patron.name == patron).first()
            rose_obj = db.session.query(Rose).join(Patron).filter(Patron.name == patron).first()
            if rose_obj and intention:
                new_user.intentions.append(intention)
                asso = AssociationUR(status="ACTIVE", rose=rose_obj, user=new_user)
                mystery = db.session.query(Mystery).filter_by(name=mystery).first()
                prayer = Prayer(mystery_id=mystery.id, ends=rose_obj.ends)
                asso.prayers.append(prayer)
                db.session.add(asso)
        db.session.commit()

if __name__ == "__main__":
    dbs = manager.Manager()
    wrong = get_wrong_users(dbs, read_user_list())
    print wrong
