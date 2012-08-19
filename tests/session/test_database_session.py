
import unittest

from webtools.database import Base
from ..settings import settings
import copy


class DatabaseSessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.application import Application

        test_settings = copy.deepcopy(settings)
        test_settings["engine_kwargs"] = {"echo": False}

        cls.app = Application([], **test_settings)
        Base.metadata.create_all(cls.app.engine)

    def test_load(self):
        self.app.session_engine.load()

        self.assertNotEqual(self.app.session_engine._current_session_key, None)
        self.assertEqual(self.app.session_engine.session_data, {})

    def test_modified(self):
        self.app.session_engine["key"] = "value"
        self.assertTrue(self.app.session_engine._modified)

    def test_save(self):
        self.app.session_engine["key"] = "value"

        self.app.session_engine.save()
        self.app.session_engine["key"] = "value2"
        self.app.session_engine.load()

        self.assertEqual(self.app.session_engine["key"], "value")

    def tearDown(self):
        self.app.session_engine.flush()
