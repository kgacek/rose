#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import MetaData, Column, Date, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

OFFSET = 12

metadata = MetaData()
Base = declarative_base(metadata=metadata)

association_table_U_I = Table('association_u_i', Base.metadata, Column('users_id', String(50), ForeignKey('users.id')),
                              Column('intentions_id', String(60), ForeignKey('intentions.id')))


class AssociationUR(Base):
    __tablename__ = 'association_u_r'
    user_id = Column(String(50), ForeignKey('users.id'), primary_key=True)
    rose_id = Column(Integer, ForeignKey('roses.id'), primary_key=True)
    status = Column(String(50))
    rose = relationship('Rose', back_populates="users")
    user = relationship('User', back_populates="roses")
    prayers = relationship('Prayer', back_populates="association", order_by="Prayer.id")


class User(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True)
    status = Column(String(50))  # NEW, VERIFIED, ACTIVE, OBSOLETE
    intentions = relationship("Intention", secondary=association_table_U_I, back_populates="users")
    roses = relationship("AssociationUR", back_populates="user")


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
    started = Column(Date)
    ends = Column(Date)
    patron = relationship("Patron", back_populates='rose')
    intention = relationship("Intention", back_populates="roses")
    users = relationship("AssociationUR", back_populates="rose")


class Mystery(Base):
    __tablename__ = 'mysteries'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Prayer(Base):
    __tablename__ = 'prayers'
    id = Column(Integer, primary_key=True)
    mystery_id = Column(Integer, ForeignKey("mysteries.id"))
    user_id = Column(String(50), ForeignKey('association_u_r.user_id'))
    association = relationship("AssociationUR", back_populates="prayers")
