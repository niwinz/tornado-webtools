# -*- coding: utf-8 -*-

import tornado.web
from .utils.imp import load_class


class Application(tornado.web.Application):
    _engine = None
    _jinja_env = None

    def __init__(self, handlers=None, default_host="", transforms=None, wsgi=False, **settings):
        handlers = self._setup_handlers(handlers)

        super(Application, self).__init__(handlers=handlers, default_host=default_host,
            transforms=transforms, wsgi=wsgi, **settings)

        self._setup_database_engine()
        self._setup_template_engine()

    def _setup_handlers(self, handlers):
        return [(x, load_class(y)) for x,y in handlers]

    def _setup_database_engine(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker

        engine_url = self.settings.get('engine_url', None)
        engine_kwargs = self.settings.get('engine_kwargs', {})

        if not engine_url:
            return

        self._engine = create_engine(engine_url, **engine_kwargs)
        self.db = scoped_session(sessionmaker(bind=self._engine))

    def _setup_template_engine(self):
        from jinja2 import Environment, PackageLoader, ChoiceLoader

        template_dirs = self.settings.get('template_dirs', [])
        if not template_dirs:
            raise RuntimeError("Missing `template_dirs` setting")

        loaders = [PackageLoader(*args) for args in template_dirs]

        jinja_settings = self.settings.get('jinja_settings', {})
        jinja_settings.setdefault("cache_size", 100)

        self._jinja_env = Environment(loader=ChoiceLoader(loaders), **jinja_settings)

    # Template system methods

    def get_template(self, template_name):
        return self._jinja_env.get_template(template_name)
