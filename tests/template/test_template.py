from webtools.template.handlers import ResponseHandlerMixin
from webtools.handlers.i18n import TimezoneMixin, I18nMixin
from webtools.handlers.base import BaseHandler
from webtools.database import Base
from webtools.utils import timezone

from ..settings import TestOverwriteSettings

from unittest import TestCase
import os.path, io
import unittest
import datetime
import pytz


class ResponseMock(ResponseHandlerMixin, I18nMixin, TimezoneMixin, BaseHandler):
    buffer = io.StringIO()
    context_processors = []

    def __init__(self):
        pass

    def write(self, chuck):
        self.buffer.write(chuck)

    def get_current_user(self):
        return None


class DefaultTemplateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.application import Application
        cls.app = Application(TestOverwriteSettings())

    def setUp(self):
        self.handler = ResponseMock()
        self.handler.application = self.app

    def test_render(self):
        self.handler.render("test.html", {"name":"foo"})
        result = self.handler.buffer.getvalue()
        self.assertEqual(result, "Hello foo")

    def test_render_to_string(self):
        result = self.handler.render_to_string("test.html", {"name": "foo"})
        self.assertEqual(result, "Hello foo")


class TimezoneModuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.application import Application
        cls.app = Application(TestOverwriteSettings())
        Base.metadata.create_all(cls.app.engine)

    def setUp(self):
        self.handler = ResponseMock()
        self.handler.application = self.app

    def tearDown(self):
        self.handler.session.flush()

    def test_activate(self):
        self.handler.activate_locale("America/Los_Angeles")
        self.assertIn("webtools_locale", self.handler.session)
        self.assertEqual("America/Los_Angeles", self.handler.session["webtools_locale"])

    def test_as_localtime(self):
        now_value = timezone.now()
        self.assertTrue(timezone.is_aware(now_value))

        self.handler.activate_locale("Europe/Madrid")
        new_value = timezone.as_localtime(now_value, self.handler.timezone)

        tzinfo = pytz.timezone("Europe/Madrid")
        self.assertNotEqual(new_value.tzinfo, tzinfo)

    def test_make_aware(self):
        dt = datetime.datetime.utcnow()
        dt = timezone.make_aware(dt, timezone.utc)

        self.assertTrue(timezone.is_aware(dt))

    def test_make_naive(self):
        dt = timezone.now()
        dt = timezone.make_naive(dt, pytz.timezone("Europe/Madrid"))

        self.assertTrue(timezone.is_naive(dt))


class TranslationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.application import Application
        cls.app = Application(TestOverwriteSettings())
        Base.metadata.create_all(cls.app.engine)

    def setUp(self):
        self.handler = ResponseMock()
        self.handler.application = self.app

    def tearDown(self):
        self.handler.session.flush()

    def test_template_translation(self):
        self.handler.activate_locale("en-US")
        template = self.handler.get_template_from_string("{{ _('privet') }}")
        result = self.handler.render_to_string(template)

        self.assertEqual(result, "hello")

        self.handler.activate_locale("es")
        template = self.handler.get_template_from_string("{{ _('privet') }}")
        result = self.handler.render_to_string(template)

        self.assertEqual(result, "hola")


