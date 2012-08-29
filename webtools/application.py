# -*- coding: utf-8 -*-

import tornado.web
import copy

from .utils.imp import load_class



class Application(tornado.web.Application):
    engine = None
    session_engine = None
    jinja_env = None

    def __init__(self, handlers=[], settings_module='webtools.settings.settings'):
        handlers = self._setup_handlers(handlers) or None
        self.conf = load_class(settings_module)

        tornado_settings = copy.deepcopy(self.conf.TORNADO_SETTINGS)
        tornado_settings.update({"cookie_secret": self.conf.SECRET_KEY})

        super(Application, self).__init__(handlers=handlers, default_host=self.conf.TORNADO_DEFAULT_HOST,
            transforms=self.conf.TORNADO_TRANSFORMS, wsgi=self.conf.TORNADO_WSGI_MODE, **tornado_settings)

        self._setup_database_engine()
        self._setup_template_engine()
        self._setup_session_engine()
        self._setup_authentication_engine()

    def _setup_handlers(self, handlers):
        return [(x, load_class(y)) for x,y in handlers]

    def _setup_database_engine(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker

        engine_url = self.conf.SQLALCHEMY_ENGINE_URL
        engine_kwargs = self.conf.SQLALCHEMY_ENGINE_KWARGS

        if not engine_url:
            return

        self.engine = create_engine(engine_url, **engine_kwargs)
        self.db = scoped_session(sessionmaker(bind=self.engine))

    def _setup_template_engine(self):
        from jinja2 import Environment, PackageLoader, ChoiceLoader, FileSystemLoader

        template_dirs = self.conf.JINJA2_TEMPLATE_DIRS
        if template_dirs is None:
            raise RuntimeError("Missing `JINJA2_TEMPLATE_DIRS` setting")

        loaders = []
        for params in template_dirs:
            if isinstance(params, str):
                loaders.append(FileSystemLoader(params))
                continue

            elif isinstance(params, (tuple, list, set)):
                if len(params) == 2:
                    loaders.append(PackageLoader(*params))
                    continue

            raise RuntimeError("Invalid JINJA2_TEMPLATE_DIRS variable on settings")

        jinja_settings = self.conf.JINJA2_SETTINGS
        self.jinja_env = Environment(loader=ChoiceLoader(loaders), **jinja_settings)

    # Session methods

    def _setup_session_engine(self):
        if not self.conf.SESSION_ENGINE:
            return

        klass = load_class(self.conf.SESSION_ENGINE)
        self.session_engine = klass(self, **self.conf.SESSION_ENGINE_KWARGS)

    # Authentication methods

    def _setup_authentication_engine(self):
        if not self.conf.AUTHENTICATION_BACKENDS:
            return

        assert isinstance(self.conf.AUTHENTICATION_BACKENDS, (tuple, list)), \
            "auth_backends must be a list or tuple"

        self._auth_backends = [load_class(x)(self) for x in self.conf.AUTHENTICATION_BACKENDS]

    def _authenticate(self, username=None, password=None):
        for backend in self._auth_backends:
            user = backend.authenticate(username=username, password=password)
            if user:
                return user

        return None
