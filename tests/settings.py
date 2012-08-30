
from webtools.settings import Settings
import os.path

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

class TestOverwriteSettings(Settings):
    SQLALCHEMY_ENGINE_URL = "sqlite://"
    AUTHENTICATION_BACKENDS = ["webtools.auth.backends.DatabaseAuthenticationBackend"]

    JINJA2_TEMPLATE_DIRS = [
        os.path.join(CURRENT_PATH, "template")
    ]

    COMMANDS = [
        "webtools.management.commands.runserver.RunserverCommand",
    ]
