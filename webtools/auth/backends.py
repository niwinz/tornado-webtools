
from

class BaseAuthenticationBackend(object):
    def __init__(self, application):
        self.application = application

    def authenticate(self, username=None, password=None):
        raise NotImplementedError()


class DatabaseAuthenticationBackend(BaseAuthenticationBackend):
    def authenticate(self, username=None, password=None):
        pass
