import unittest
import datetime
import pytz

class TimezoneModuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.utils import timezone
        cls.tz = timezone

    def setUp(self):
        self.tz.set_default_timezone_name("Europe/Madrid")
        self.tz.activate("Europe/Madrid")

    def test_activate(self):
        self.tz.activate("America/Los_Angeles")
        self.assertEqual(self.tz.get_current_timezone_name(), "America/Los_Angeles")

    def test_deactivate(self):
        self.tz.activate("America/Los_Angeles")
        self.assertTrue(hasattr(self.tz._active, "value"))

        self.tz.deactivate()
        self.assertFalse(hasattr(self.tz._active, "value"))

    def test_as_localtime(self):
        value = self.tz.now()
        self.assertTrue(self.tz.is_aware(value))

        tzinfo = pytz.timezone("Europe/Madrid")

        value = self.tz.as_localtime(value)
        self.assertNotEqual(value.tzinfo, self.tz.utc)

    def test_make_aware(self):
        dt = datetime.datetime.utcnow()
        dt = self.tz.make_aware(dt, self.tz.utc)

        self.assertTrue(self.tz.is_aware(dt))

    def test_make_naive(self):
        dt = self.tz.now()
        dt = self.tz.make_naive(dt, pytz.timezone("Europe/Madrid"))

        self.assertTrue(self.tz.is_naive(dt))
