
from webtools.settings import settings

class TestOverwriteSettings(settings):
    SQLALCHEMY_ENGINE_URL = "sqlite://"
