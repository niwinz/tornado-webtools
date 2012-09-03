# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table, select
from sqlalchemy.types import Integer, PickleType, DateTime, Unicode

from webtools.database import Base
from webtools.utils import timezone
from .base import BaseSessionEngine


session = Table("webtools_session", Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=False),
    Column("last_modify", DateTime(timezone=True), index=True),
    Column("key", Unicode(length=100), unique=True, index=True),
    Column("data", PickleType, unique=True),
)

class DatabaseEngine(BaseSessionEngine):
    @property
    def db(self):
        return self._application.db

    def load(self):
        if self._current_session_key is None:
            self._current_session_key = self.random_session_key()

            sql = session.insert().values(
                last_modify = timezone.now(),
                key = self._current_session_key,
                data = {}
            )

            self.db.execute(sql)
            self._session_data = {}
            self._modified = False
        else:
            sql = select([session.c.key, session.c.data]).where(session.c.key == self._current_session_key)
            res_proxy = self.db.execute(sql).first()
            if res_proxy:
                self._session_data = res_proxy['data']
                self._modified = False

    def save(self):
        sql = session.update()\
            .where(session.c.key == self._current_session_key)\
            .values(data=self._session_data)

        self.db.execute(sql)
        self.db.commit()

        self._modified = False

    def delete(self):
        if self._current_session_key is None:
            return

        self.db.execute(session.delete().where(session.c.key == self._current_session_key))
        self.db.commit()

        self._current_session_key = None
        self._session_data = None
