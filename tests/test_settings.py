import unittest

class SampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.settings import settings
        cls.settings = settings


    def test_access_undefined(self):
        self.assertEqual(self.settings.FOO, None)

    def test_access_some_default(self):
        self.assertEqual(self.settings.TORNADO_SETTINGS, {})

    def test_overwrite_1(self):
        class mysettings(self.settings):
            TORNADO_SETTINGS = {"foo": "bar"}

        self.assertEqual(self.settings.TORNADO_SETTINGS, {"foo": "bar"})
        self.settings.clear_to_default()
        self.assertEqual(self.settings.TORNADO_SETTINGS, {})

    def test_overwrite_2(self):
        self.settings.configure({
            "TORNADO_SETTINGS": {"foo": "bar"}
        })

        self.assertEqual(self.settings.TORNADO_SETTINGS, {"foo": "bar"})
        self.settings.clear_to_default()
        self.assertEqual(self.settings.TORNADO_SETTINGS, {})
