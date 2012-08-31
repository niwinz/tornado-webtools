# -*- coding: utf-8 -*-

from .models import User


class AuthHandlerMixin(object):
    def authenticate(self, username, password):
        user = self.application.authenticate(username=username, password=password)
        if user is not None:
            self.session["user_id"] = user.id

    def get_current_user(self):
        if hasattr(self, "_user"):
            return self._user

        if "user_id" in self.session:
            self._user = self.db.query(User).filter(User.id == self.session["user_id"]).one()
            return self._user

        return None
