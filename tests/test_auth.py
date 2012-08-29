import unittest

from webtools.database import Base
from webtools.auth.models import User

from .settings import settings


class AuthDatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from webtools.application import Application

        cls.app = Application(settings_module="tests.settings.TestOverwriteSettings")
        Base.metadata.create_all(cls.app.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.app.engine)

    def tearDown(self):
        self.app.db.query(User).delete()
        self.app.db.commit()

    def test_authenticate(self):
        u = User(username="foo", first_name="", last_name="", email="foo@bar.com")
        u.set_password("bar")
        self.app.db.add(u)

        authenticated_user = self.app._authenticate(username="foo", password="bar")
        self.assertEqual(u.id, authenticated_user.id)

