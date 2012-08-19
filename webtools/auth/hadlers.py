# -*- coding: utf-8 -*-

from .models import User


class AuthHandlerMixin(object):
    def authenticate(self, username, password):
        user = self.application.authenticate(username=username, password=password)
        if user is not None:
            self.session["user_id"] = user.id

    @property
    def current_user(self):
        if "user_id" in self.session:
            return self.db.query(User).filter(User.id == self.session["user_id"]).one()
        return None
