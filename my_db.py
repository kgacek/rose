from sqlalchemy import MetaData, create_engine, Column, Date, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import yaml

metadata = MetaData()
Base = declarative_base(metadata=metadata)

association_table_U_R = Table('association_u_r', Base.metadata, Column('users_id', String(50), ForeignKey('users.id')),
                              Column('roses_id', Integer, ForeignKey('roses.id')))
association_table_U_I = Table('association_u_i', Base.metadata, Column('users_id', String(50), ForeignKey('users.id')),
                              Column('intentions_id', String(60), ForeignKey('intentions.id')))


class User(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True)
    status = Column(String(50))  # NEW, VERIFIED, ACTIVE, SUBSCRIBED, OBSOLETE
    intentions = relationship("Intention", secondary=association_table_U_I, back_populates="users")
    roses = relationship("Rose", secondary=association_table_U_R, back_populates="users")
    prayers = relationship("Prayer", back_populates="user")


class Intention(Base):
    __tablename__ = 'intentions'
    id = Column(String(60), primary_key=True)
    name = Column(String(100))
    roses = relationship("Rose", back_populates="intention")
    users = relationship("User", secondary=association_table_U_I, back_populates="intentions")


class Patron(Base):
    __tablename__ = 'patrons'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    rose = relationship("Rose", uselist=False, back_populates="patron")


class Rose(Base):
    __tablename__ = 'roses'
    id = Column(Integer, primary_key=True)
    patron_id = Column(Integer, ForeignKey("patrons.id"))
    intention_id = Column(String(60), ForeignKey("intentions.id"))
    patron = relationship("Patron", back_populates='rose')
    intention = relationship("Intention", back_populates="roses")
    users = relationship("User", secondary=association_table_U_R, back_populates="roses")
    prayers = relationship("Prayer", back_populates="rose")


class Mystery(Base):
    __tablename__ = 'mysteries'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Prayer(Base):
    __tablename__ = 'prayers'
    id = Column(Integer, primary_key=True)
    mystery_id = Column(Integer, ForeignKey("mysteries.id"))
    started = Column(Date)
    ends = Column(Date)
    rose_id = Column(Integer, ForeignKey("roses.id"))
    user_id = Column(String(50), ForeignKey('users.id'))
    user = relationship("User", back_populates="prayers")
    rose = relationship("Rose", back_populates="prayers")


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
            rose = Rose(intention_id=intention)
            rose.patron = pat
            session.add(rose)

    # add patrons
    for el in in_data['patrons']:
        session.add(Patron(name=el))

    for el in in_data['mysteries']:
        session.add(Mystery(name=el))

    session.commit()

def get_not_confirmed_users(offset=5):
    session = Session()
    expiring_prayers = session.query(Prayer).filter(Prayer.ends - timedelta(days=offset) < date.today()).all()
    msg = {}
    for prayer in expiring_prayers:
        if prayer.user and prayer.user.status == "ACTIVE":
            msg[prayer.user_id] = prayer.rose.patron.name
    session.close()
    return msg


def switch_users():
    session = Session()
    subscribed_users = session.query(User).filter(User.status == "SUBSCRIBED").all()
    msg = {}
    for user in subscribed_users:
        msg[user.id] = []
        prayers = session.query(Prayer).filter_by(user_id=user.id).filter(Prayer.ends == date.today()).all()
        for prayer in prayers:
            new = Prayer(mystery_id=prayer.mystery_id % 20 + 1,
                         started=date.today(),
                         ends=date.today() + relativedelta(months=1),
                         rose=prayer.rose,
                         user=user)
            session.add(new)
            msg[user.id].append({'mystery_id': new.mystery_id, 'rose': new.rose.patron.name})
    session.commit()
    return msg


def get_unsubscribed_users():
    pass
