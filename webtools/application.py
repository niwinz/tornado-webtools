# -*- coding: utf-8 -*-

import tornado.web
from .utils.imp import load_class

DEFAULT_SESSION_ENGINE = 'webtools.session.backend.database.DatabaseEngine'


class Application(tornado.web.Application):
    engine = None
    session_engine = None
    jinja_env = None

    def __init__(self, handlers=None, default_host="", transforms=None, wsgi=False, **settings):
        handlers = self._setup_handlers(handlers)

        super(Application, self).__init__(handlers=handlers, default_host=default_host,
            transforms=transforms, wsgi=wsgi, **settings)

        self._setup_database_engine()
        self._setup_template_engine()
        self._setup_session_engine()
        #self._setup_authentication_engine()

    def _setup_handlers(self, handlers):
        return [(x, load_class(y)) for x,y in handlers]

    def _setup_database_engine(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker

        engine_url = self.settings.get('engine_url', None)
        engine_kwargs = self.settings.get('engine_kwargs', {})

        if not engine_url:
            return

        self.engine = create_engine(engine_url, **engine_kwargs)
        self.db = scoped_session(sessionmaker(bind=self.engine))

    def _setup_template_engine(self):
        from jinja2 import Environment, PackageLoader, ChoiceLoader

        template_dirs = self.settings.get('template_dirs', [])
        if template_dirs is None:
            raise RuntimeError("Missing `template_dirs` setting")

        loaders = [PackageLoader(*args) for args in template_dirs]

        jinja_settings = self.settings.get('jinja_settings', {})
        jinja_settings.setdefault("cache_size", 100)

        self.jinja_env = Environment(loader=ChoiceLoader(loaders), **jinja_settings)

    # Session methods

    def _setup_session_engine(self):
        if "session_engine" not in self.settings:
            self.settings["session_engine"] = DEFAULT_SESSION_ENGINE

        if "session_engine_kwargs" not in self.settings:
            self.settings["session_engine_kwargs"] = {}

        klass = load_class(self.settings['session_engine'])
        self.session_engine = klass(self, **self.settings["session_engine_kwargs"])

    # Authentication methods

    def _setup_authentication_engine(self):
        assert "auth_backends" in self.settings, "auth_backends settings is not defined"
        assert isinstance(self.settings['auth_backends'], (tuple, list)), \
            "auth_backends must be a list or tuple"
        assert len(self.settings['auth_backends']) > 0, "auth_backends must contains almost one backend"

        self._auth_backends = [load_class(x)() for x in self.settings['auth_backends']]

    def authenticate(self, **credentials):
        for backend in self._auth_backends:
            try:
                user = backend.authenticate(**credentials)
            except (TypeError, NotImplementedError):
                continue

            if user is None:
                continue

            return user

    # Template system methods

    def get_template(self, template_name):
        return self._jinja_env.get_template(template_name)
