from sqlalchemy import create_engine, Column, DateTime, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True)
    active_from = Column(DateTime)
    current_prayer_id = Column(Integer)
    prayer = relationship(

class Rose(Base):
    __tablename__ = 'roses'
    id = Column(Integer, primary_key=True)


class Mystery(Base):
    __tablename__ = 'mysteries'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

class Intetnion(Base):
    __tablename__ = 'intentions'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

class Prayer(Base):
    __tablename__ = 'prayers'
    id = Column(Integer, primary_key=True)
    mystery_id = Column(Integer)
    intention_id = Column(Integer)
    user_id = Column(Integer)
    user_counter = Column(Integer)


engine = create_engine("mysql://kgacek:kaszanka12@kgacek.mysql.pythonanywhere-services.com/kgacek$roza", echo=True)
#Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def add_user(user_id):
    session = Session()
    if session.query(User).filter_by(id=user_id).first():
        return False
    session.add(User(id=user_id,active_from=datetime.datetime.today()))
    session.commit()
    return True
