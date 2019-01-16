from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import yaml

Base = declarative_base()

association_table_U_R = Table('association_u_r', Base.metadata, Column('users_id', String(50), ForeignKey('users.id')),
                              Column('roses_id', Integer, ForeignKey('roses.id')))
association_table_U_I = Table('association_u_i', Base.metadata, Column('users_id', String(50), ForeignKey('users.id')),
                              Column('intentions_url', String(60), ForeignKey('intentions.url')))


class User(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True)
    status = Column(String(50))
    intentions = relationship("Intention", secondary=association_table_U_I, back_populates="users")
    roses = relationship("Rose", secondary=association_table_U_R, back_populates="users")
    prayers = relationship("Prayer", back_populates="user")


class Intention(Base):
    __tablename__ = 'intentions'
    url = Column(String(60), primary_key=True)
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
    intention_url = Column(String(60), ForeignKey("intentions.url"))
    patron = relationship("Patron", back_populates='rose')
    intention = relationship("Intention", back_populates="roses")
    users = relationship("User", secondary=association_table_U_R, back_populates="roses")


class Mystery(Base):
    __tablename__ = 'mysteries'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Prayer(Base):
    __tablename__ = 'prayers'
    id = Column(Integer, primary_key=True)
    mystery_id = Column(Integer, ForeignKey("mysteries.id"))
    rose_id = Column(Integer, ForeignKey("roses.id"))
    user_id = Column(String(50), ForeignKey('users.id'))
    user = relationship("User", back_populates="prayers")


engine = create_engine("mysql://kgacek:kaszanka12@kgacek.mysql.pythonanywhere-services.com/kgacek$roza?charset=utf8", echo=True)
# Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def fill_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session()
    with open('input_data.yaml') as f:
        in_data = yaml.load(f)

    #add intentions
    for el in in_data['intentions']:
        session.add(Intention(url=in_data['intentions'][el], name=el))

    #add roses with patrons
    for intention in in_data['roses']:
        for patron in in_data['roses'][intention]:
            pat = Patron(name=patron)
            rose = Rose(intention_url=intention)
            rose.patron = pat
            session.add(rose)

    #add patrons
    for el in in_data['patrons']:
        session.add(Patron(name=el))

    for el in in_data['mysteries']:
        session.add(Mystery(name=el))

    session.commit()


def add_user(user_id):
    session = Session()
    if session.query(User).filter_by(id=user_id).first():
        return False
    session.add(User(id=user_id, status="PENDING"))
    session.commit()
    return True


def subscribe_user(user_id):
    pass


def unsubscribe_user(user_id):
    pass


def get_unsubscribed_users():
    pass
