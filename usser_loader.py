from collections import defaultdict
import re
import manager
from my_db import Intention, Prayer, Rose, Patron, Mystery, User, AssociationUR
from fuzzywuzzy import fuzz


def read_user_list(user_map):
    all_users = defaultdict(list)
    verified_users = []
    with open('all_users.csv') as f:
        for line in f:
            list_line = line.strip('\r\n').split(',')
            if list_line:
                if not list_line[1] and list_line[0]:
                    key = list_line[0]
                elif list_line[1] and list_line[0] and list_line[2]:
                    username, mystery, url = list_line
                    macz = re.match(r'^\d+.?(.*)', username)
                    if macz:
                        username = macz.group(1).strip()
                    macz2 = re.search(r'(.*)\(', username)
                    if macz2:
                        username = macz2.group(1).strip()
                    if url != '0':
                        verified_users.append(username)
                    username = user_map.get(username.strip(',. '), username.strip(',. '))
                    all_users[username].append((key, mystery.strip('"- ')))
    return all_users, verified_users


def get_wrong_users(db, all_users):

    wrong = defaultdict(list)
    db_users = db.session.query(User).all()
    for user, mysteries in all_users.items():
        db_user = [usr for usr in db_users if usr.fullname==user]
        if len(db_user)>1:
            print('uwaga')
            continue
        if db_user:
            if len(db_user[0].roses) != len(mysteries):
                wrong[user].append('rózna ilość róż')
            for patron, mystery in mysteries:
                match = [rose for rose in db_user[0].roses if rose.rose.patron.name == patron]
                if not match:
                    wrong[user].append(patron)
                elif match[0].prayers[-1].mystery.name.lower() != mystery.lower():
                    wrong[user].append((patron, mystery))
    return wrong


def add_new_users(db, all_users):
    for user, mysteries in all_users.items():
        add_new_user(db, user, mysteries)


def add_new_user(db, user, mysteries):
    myst = {}
    for patron, mystery in mysteries:
        if patron not in myst:
            myst[patron] = mystery
        else:
            print('uwaga,zdublowany patron')
    db_users = db.session.query(User).filter_by(fullname=user).all()
    if len(db_users) > 1:
        print('uwaga')
        return
    if not db_users:
        db_user = User(global_id=user, fullname=user, status='ACTIVE')
    else:
        db_user = db_users[0]
        db.unsubscribe_user(db_user.global_id)
    for patron, mystery in myst.items():
        intention = db.session.query(Intention).join(Rose).join(Patron).filter(Patron.name == patron).first()
        rose_obj = db.session.query(Rose).join(Patron).filter(Patron.name == patron).first()
        if rose_obj and intention:
            db_user.intentions.append(intention)
            asso = AssociationUR(status="ACTIVE", rose=rose_obj, user=db_user)
            mystery = db.session.query(Mystery).filter_by(name=mystery).first()
            prayer = Prayer(mystery_id=mystery.id, ends=rose_obj.ends)
            asso.prayers.append(prayer)
            db.session.add(asso)
    db.session.commit()


def find_simillar(users, verified):
    sim= defaultdict(list)  # username - similar usernames
    sim2 = defaultdict(list)  # username - probably simmilar usernames
    ver = defaultdict(list)  # good username - wrong usernames
    ver2 = defaultdict(list)  # good username - probably wrong usernames
    for user in users:
        for comp in users:
            ratio = fuzz.ratio(user, comp)
            if 89 < ratio < 99:
                if user in verified:
                    ver[user].append((comp, ratio))
                elif comp not in verified:
                    sim[user].append((comp, ratio))
            elif 84 < ratio < 90:
                if user in verified:
                    ver2[user].append((comp, ratio))
                elif comp not in verified:
                    sim2[user].append((comp, ratio))

    sim = dict(sim)
    sim2 = dict(sim2)
    print(sim2)
    print(ver2)
    print(sim)
    print(ver)
    return sim


def check_db(db, sim, sim2):
    db_users = db.session.query(User).all()
    ver = {}  # good username - wrong usernames
    ver2 = {}  # good username - probably wrong usernames
    for user in sim:
        db_user = [usr for usr in db_users if usr.fullname == user]
        if db_user:
            ver[user] = list(sim[user])
    for user in sim2:
        db_user = [usr for usr in db_users if usr.fullname == user]
        if db_user:
            ver2[user] = list(sim2[user])

    for v in ver:
        del sim[v]
    for v in ver2:
        del sim2[v]

    for user in sim:
        sim[user] = [el for el in sim[user] if el[0] not in ver]
    for user in sim2:
        sim2[user] = [el for el in sim2[user] if el[0] not in ver2]

    print(sim2)
    print(ver2)
    print(sim)
    print(ver)
    return sim


def read_map():
    with open('pewniaki.csv') as f:
        d = {}
        for line in f:
            lst = line.split(',')
            if len(lst) > 2 and lst[0] and lst[1]:
                d[lst[1]] = lst[0]
    return d


if __name__ == "__main__":
    dbs = manager.Manager()
    user_map = read_map()
    users, verified = read_user_list(user_map)
    #db_users = dbs.session.query(User).all()
    #d=[user.fullname for user in db_users if user.fullname not in users.keys()]
    add_new_users(dbs, users)
   # wrong = get_wrong_users(dbs, users)
    #print(wrong)
