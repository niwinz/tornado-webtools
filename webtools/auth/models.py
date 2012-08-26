# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.types import Integer, String, DateTime, Unicode

from webtools.database import Base
from webtools.auth.hashers import make_password


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autonumeric=True)
    username = Column(Unicode(200), nullable=False, index=True)
    first_name = Column(Unicode(200), nullable=False)
    last_name = Column(Unicode(200), nullable=False)
    email = Column(Unicode(200), nullable=False)
    password = Column(String(200), nullable=False)

    def __repr__(self):
        return "<User {0}>".format(self.id)

    def set_password(self, password):
        self.password = make_password(password)
