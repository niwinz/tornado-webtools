# -*- coding: utf-8 -*-

import tornado.web
import copy
import importlib

from .utils.imp import load_class
from .template.base import Library


_global_app = None

def get_app():
    global _global_app
    if _global_app is None:
        raise RuntimeError("Application is not initialized")

    return _global_app

def set_app(_app):
    global _global_app
    _global_app = _app

def del_app():
    global _global_app
    _global_app = None


class Application(tornado.web.Application):
    engine = None
    session_engine = None
    jinja_env = None

    auth_backends = []
    context_processors = []

    def __init__(self, settings):
        self.conf = settings

        handlers = self.conf.HANDLERS
        if handlers is not None:
            try:
                handlers = load_class(handlers + ".patterns")
            except ImportError:
                raise RuntimeError("Cannot import  handlers path: {0}".format(handlers))
            handlers = self._setup_handlers(handlers) or None

        tornado_settings = copy.deepcopy(self.conf.TORNADO_SETTINGS)
        tornado_settings.update({"cookie_secret": self.conf.SECRET_KEY})

        super(Application, self).__init__(handlers=handlers, default_host=self.conf.TORNADO_DEFAULT_HOST,
            transforms=self.conf.TORNADO_TRANSFORMS, wsgi=self.conf.TORNADO_WSGI_MODE, **tornado_settings)

        self._setup_database_engine()
        self._setup_session_engine()
        self._setup_authentication_engine()
        self._setup_template_loaders()
        self._setup_installed_modules()
        self._setup_template_engine()

        set_app(self)

    def _setup_handlers(self, handlers):
        if handlers is None:
            return None
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

    def _setup_i18n(self):
        if self.conf.I18N:
            if self.conf.I18N_DIRECTORY is None:
                raise RuntimeError("I18N_DIRECTORY must be a valid directory")

            from tornado import locale
            locale.set_default_locale(self.conf.I18N_DEFAULT_LANG)
            locale.load_gettext_translations(self.conf.I18N_DIRECTORY, self.conf.I18N_DOMAIN)

    def _setup_installed_modules(self):
        # initialize app level variables
        from jinja2 import PackageLoader
        self.models_modules = []

        if not self.conf.INSTALLED_MODULES:
            raise RuntimeError("INSTALLED_MODULES is mandatory setting.")

        # setup module template loader
        for module_path in self.conf.INSTALLED_MODULES:
            print("Setup {0} module...".format(module_path))

            module = None
            try:
                module = importlib.import_module(module_path)
            except ImportError:
                continue

            # setup module template loader
            self.loaders.append(PackageLoader(module_path, "templates"))

            # setup jinja template additions
            try:
                importlib.import_module(module_path + ".jinja2_addons")
            except ImportError:
                pass

            # try import models
            try:
                models_mod = importlib.import_module(module_path + ".models")
                self.models_modules.append(models_mod)
            except ImportError:
                pass

        if Library._instance:
            Library._instance._update_env(self.jinja_env)

    def _setup_template_loaders(self):
        """
        Initialize loaders variable and add fixed
        user defined template dirs with FileSystemLoader.
        """

        from jinja2 import FileSystemLoader
        template_dirs = self.conf.JINJA2_TEMPLATE_DIRS
        if template_dirs is None:
            raise RuntimeError("Missing `JINJA2_TEMPLATE_DIRS` setting")

        self.loaders = []
        for params in template_dirs:
            if isinstance(params, str):
                self.loaders.append(FileSystemLoader(params))
                continue

            raise RuntimeError("Invalid JINJA2_TEMPLATE_DIRS variable on settings")

    def _setup_template_engine(self):
        from jinja2 import Environment, ChoiceLoader

        self.jinja_env = Environment(loader=ChoiceLoader(self.loaders),
            **self.conf.JINJA2_SETTINGS)

        # load context processors
        context_processors = self.conf.JINJA2_CONTEXT_PROCESSORS or []
        self.context_processors = [load_class(x) for x in context_processors]

    def _setup_session_engine(self):
        if not self.conf.SESSION_ENGINE:
            return

        klass = load_class(self.conf.SESSION_ENGINE)
        self.session_engine = klass(self, **self.conf.SESSION_ENGINE_KWARGS)

    def _setup_authentication_engine(self):
        if not self.conf.AUTHENTICATION_BACKENDS:
            return

        assert isinstance(self.conf.AUTHENTICATION_BACKENDS, (tuple, list)), \
            "auth_backends must be a list or tuple"

        self.auth_backends = [load_class(x)(self) for x in self.conf.AUTHENTICATION_BACKENDS]
        if self.session_engine is None:
            raise RuntimeError("Auth subsystem works only with session")

        # Add auth context processor to global list
        self.conf.JINJA2_CONTEXT_PROCESSORS.append("webtools.auth.context_processors.auth")

    def _authenticate(self, username=None, password=None):
        for backend in self.auth_backends:
            user = backend.authenticate(username=username, password=password)
            if user:
                return user

        return None
