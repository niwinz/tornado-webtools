import unittest

class SampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.settings import Settings
        cls.settings = Settings()

    def test_access_undefined(self):
        self.assertEqual(self.settings.FOO, None)

    def test_access_some_default(self):
        self.assertEqual(self.settings.TORNADO_SETTINGS, {})

    def test_overwrite_1(self):
        self.settings.configure({
            "TORNADO_SETTINGS": {"foo": "bar"}
        })

        self.assertEqual(self.settings.TORNADO_SETTINGS, {"foo": "bar"})
        self.settings.clear_to_default()
        self.assertEqual(self.settings.TORNADO_SETTINGS, {})
