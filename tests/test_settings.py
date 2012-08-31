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

    def test_subclasses(self):
        from webtools.settings import Settings

        class FooSettings(Settings):
            FOO = 1

        settings = FooSettings()
        self.assertEqual(settings.FOO, 1)
        self.assertEqual(settings.FOO2, None)

        class Foo2Settings(FooSettings):
            FOO = 2

        settings = Foo2Settings()
        self.assertEqual(settings.FOO, 2)
        self.assertEqual(settings.FOO2, None)
