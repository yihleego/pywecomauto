# -*- coding: utf-8 -*-
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DIR, r'pywecomauto.db3')
ENGINE = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, echo=False)


def open_session():
    return sessionmaker(bind=ENGINE)()
