
from webtools.settings import settings
import os.path

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

class TestOverwriteSettings(settings):
    SQLALCHEMY_ENGINE_URL = "sqlite://"

    JINJA2_TEMPLATE_DIRS = [
        os.path.join(CURRENT_PATH, "template")
    ]
