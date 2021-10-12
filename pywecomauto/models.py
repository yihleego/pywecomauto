# -*- coding: utf-8 -*-
from enum import IntEnum


class TaskType(IntEnum):
    CHECK = -1
    LOGIN = 0
    LOGOUT = 1
    CONTACT = 2
    PERSONAL_MESSAGE = 3
    GROUP_MESSAGE = 4


class TaskStatus(IntEnum):
    CREATED = 0
    FINISHED = 1
    RUNNING = 2
    FAILED = 3
    TIMEOUT = 4
    UNLOGGED = 5
    UNAVAILABLE = 6


class ClientStatus(IntEnum):
    OFFLINE = 0
    ONLINE = 1
    WAITING = 2
