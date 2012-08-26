from webtools.template.handlers import ResponseHandlerMixin
from unittest import TestCase
import os.path
import io

class ResponseMock(ResponseHandlerMixin, object):
    buffer = io.StringIO()

    def write(self, chuck):
        self.buffer.write(chuck)


class DefaultTemplateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.application import Application

        cls.app = Application(settings_module="tests.settings.TestOverwriteSettings")

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

