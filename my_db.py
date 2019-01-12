from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

association_table_U_R = Table('association_u_r', Base.metadata, Column('users_id', Integer, ForeignKey('users.id')),
                              Column('roses_id', Integer, ForeignKey('roses.id')))
association_table_U_I = Table('association_u_i', Base.metadata, Column('users_id', Integer, ForeignKey('users.id')),
                              Column('intentions_id', Integer, ForeignKey('intentions.id')))


class User(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True)
    status = Column(String(50))
    intentions = relationship("Intention", secondary=association_table_U_I, back_populates="users")
    roses = relationship("Rose", secondary=association_table_U_R, back_populates="users")
    prayers = relationship("Prayer", back_populates="user")
    intentions_managed = relationship("Intention", back_populates="admin")


class Intention(Base):
    __tablename__ = 'intentions'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    admin_id = Column(Integer, ForeignKey('users.id'))
    roses = relationship("Rose", back_populates="intention")
    admin = relationship("User", back_populates="intentions_managed")
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
    intention_id = Column(Integer, ForeignKey("intentions.id"))
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
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="prayers")


engine = create_engine("mysql://kgacek:kaszanka12@kgacek.mysql.pythonanywhere-services.com/kgacek$roza", echo=True)
# Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


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
