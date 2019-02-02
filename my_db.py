#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import MetaData, Column, Date, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

metadata = MetaData()
Base = declarative_base(metadata=metadata)

association_table_U_I = Table('association_u_i', Base.metadata, Column('users_psid', String(50), ForeignKey('users.psid')),
                              Column('intentions_id', String(60), ForeignKey('intentions.id')))


class AssociationUR(Base):
    """
    Class represents association table between Users and roses ( MANY-to-MANY relationship)
    additional fields:
    prayers - ONE-to-MANY relationship with prayers assigned to every user within each rose
    status:
    ACTIVE -  when user is praying in related rose
    SUBSCRIBED - when user confirm his/her prayer in each rose before rose.ends date
    EXPIRED - when user didn't subscribed to next month and rose.ends was reached
    """
    __tablename__ = 'association_u_r'
    user_psid = Column(String(50), ForeignKey('users.psid'), primary_key=True)
    rose_id = Column(Integer, ForeignKey('roses.id'), primary_key=True)
    status = Column(String(50))
    rose = relationship('Rose', back_populates="users")
    user = relationship('User', back_populates="roses")
    prayers = relationship('Prayer', back_populates="association", order_by="Prayer.id")


class User(Base):
    """
    class represents User table.
    psid - facebook Page Scoped ID - used to communicate on messenger
    global_id - App Scoped ID - received from Facebook Login
    fullname -'name surname' eg. Krzysztof Gacek
    intentions - MANY-to-MANY relationship - every user can be in many intentions, one intention can have many users
    roses - MANY-to-MANY relationship - every user can be in many roses, one rose can have many users
    status:
    NEW - after first interactions with our tool
    VERIFIED - when accepted by admin
    ACTIVE - when have at least one active rose
    OBSOLETE - when unsubscribed
    """
    __tablename__ = 'users'
    psid = Column(String(50), primary_key=True)
    global_id = Column(String(50))  # ToDo consider making this ID as a primary key
    fullname = Column(String(50))
    status = Column(String(50))
    intentions = relationship("Intention", secondary=association_table_U_I, back_populates="users")
    roses = relationship("AssociationUR", back_populates="user")


class Intention(Base):
    """Class represents Intentions table.
    id - fb group ID
    name - intention full name
    roses - ONE-to-MANY relationship -  list of roses attached to each intention
    users - MANY-to-MANY relationship - list of users which are in each intention"""
    __tablename__ = 'intentions'
    id = Column(String(60), primary_key=True)
    name = Column(String(100))
    roses = relationship("Rose", back_populates="intention")
    users = relationship("User", secondary=association_table_U_I, back_populates="intentions")


class Patron(Base):
    """Class represents Patrons Table with all Patrons for Roses.
    id  - number - autoincrement
    name - Patron name
    rose - ONE-to-ONE relationship, every Rose has its own Patron"""
    __tablename__ = 'patrons'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    rose = relationship("Rose", uselist=False, back_populates="patron")


class Rose(Base):  # ToDo consider adding Rose related numbers
    """Class represents Roses table.
    id - number - autoincrement
    ends - date when current cycle ends. - updated when new cycle starts.
    patron - ONE-to-ONE relationship, every Rose has its own Patron
    intention - MANY-to-ONE relationship -  intention where this rose is
    users - MANY-to-MANY relationship - list of users which are in each roses"""
    __tablename__ = 'roses'
    id = Column(Integer, primary_key=True)
    patron_id = Column(Integer, ForeignKey("patrons.id"))
    intention_id = Column(String(60), ForeignKey("intentions.id"))
    started = Column(Date)  # ToDo maybe it can be removed?
    ends = Column(Date)
    patron = relationship("Patron", back_populates='rose')
    intention = relationship("Intention", back_populates="roses")
    users = relationship("AssociationUR", back_populates="rose")


class Mystery(Base):
    """Class represents Mysteries in Rosary
    id - number - autoincrement
    name - Mystery name """
    __tablename__ = 'mysteries'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Prayer(Base):
    """Class represents Prayers table.
    id - number - autoincrement
    ends - date when this prayer ends.
    mystery_id -
    association - MANY-to-ONE relationship  - User-Rose pair Associated with this prayer
    """
    __tablename__ = 'prayers'
    id = Column(Integer, primary_key=True)
    ends = Column(Date)
    mystery_id = Column(Integer, ForeignKey("mysteries.id"))
    user_psid = Column(String(50), ForeignKey('association_u_r.user_psid'))
    association = relationship("AssociationUR", back_populates="prayers")
