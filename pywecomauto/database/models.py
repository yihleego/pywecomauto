# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from enum import IntEnum

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def after_seconds(s):
    return (datetime.now() + timedelta(seconds=s)).strftime("%Y-%m-%d %H:%M:%S")


def to_dict(entity):
    if hasattr(entity, '__table__'):
        return {i.name: getattr(entity, i.name) for i in entity.__table__.columns}
    else:
        return {}


def to_json(entity):
    return json.dumps(entity.to_dict())


class App(Base):
    __tablename__ = "app"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(String, default=now)
    updated_time = Column(String, onupdate=now)
    name = Column(String)
    private_key = Column(String)
    public_key = Column(String)
    url = Column(String)
    status = Column(Integer, default=0)


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(String, default=now)
    updated_time = Column(String, onupdate=now)
    expired_time = Column(String)
    process = Column(Integer, index=True)
    handle = Column(Integer, index=True)
    company_name = Column(String)
    user_name = Column(String)
    alias = Column(String)
    phone = Column(String)
    avatar = Column(String)
    status = Column(Integer, default=0)


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(String, default=now)
    updated_time = Column(String, onupdate=now)
    deleted_time = Column(String)
    scheduled_time = Column(String, default=now)
    executed_time = Column(String)
    finished_time = Column(String)
    company_name = Column(String)
    user_name = Column(String)
    type = Column(Integer)
    content = Column(String)
    result = Column(String)
    message = Column(String)
    status = Column(Integer, default=0)
    deleted = Column(Integer, default=0)


class Notification(Base):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(String, default=now)
    updated_time = Column(String, onupdate=now)
    notified_time = Column(String, default=now)
    task_id = Column(Integer)
    request = Column(String)
    response = Column(String)
    status = Column(Integer, default=0)


class TaskType(IntEnum):
    CHECK = -1
    LOGIN = 0
    LOGOUT = 1
    CONTACT = 2
    PERSONAL_MESSAGE = 3
    GROUP_MESSAGE = 4


class TaskStatus(IntEnum):
    CREATED = 0
    RUNNING = 1
    FINISHED = 2
    FAILED = 3
    TIMEOUT = 4
    UNAVAILABLE = 5


class ClientStatus(IntEnum):
    IDLE = 0
    USING = 1
    WAITING = 2


class NotificationStatus(IntEnum):
    CREATED = 0
    SUCCESS = 1
    FAILURE = 2
    IGNORED = 3


class RSAKeyType(IntEnum):
    PKCS1 = 1
    PKCS8 = 8
    PKCS12 = 12
