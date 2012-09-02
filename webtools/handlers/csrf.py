# -*- coding: utf-8 -*-

import uuid


class CsrfMixin(object):
    enforce_csrf_check = False
    current_csrf_token = None

    def prepare(self):
        super(CsrfMixin, self).prepare()

        if not self.enforce_csrf_check:
            return

        self._set_csrf_cookie()
        if self.request.method == "POST":
            self._check_csrf()

    def _set_csrf_cookie(self):
        token = self.get_cookie(self.conf.CSRF_COOKIE_NAME, default=None)
        if not token:
            token = self._generate_csrf_token()
            self.set_cookie(self.conf.CSRF_COOKIE_NAME, token,
                expires_days=2) # TODO: set this with one settings

        self.current_csrf_token = token

    def _check_csrf(self):
        # first check parameters
        csrf_value = self.get_argument(self.conf.CSRF_COOKIE_NAME, default=None)

        # fallback checks headers
        if csrf_value is None:
            csrf_value = self.get_header("X-CSRFToken")

        if csrf_value is None:
            raise HTTPError(403, "Missing csrf value")

        if csrf_value != self.current_csrf_token:
            raise HTTPError(403, "Wrong csrf value")

    def get_header(self, name, default=None):
        if name in self.request.headers:
            return self.request.headers[name]

        return default


    def _generate_csrf_token(self):
        return str(uuid.uuid1())



