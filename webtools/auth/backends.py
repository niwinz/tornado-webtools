
class BaseAuthenticationBackend(object):
    def __init__(self, application):
        self.application = application

    def authenticate(self, username=None, password=None):
        raise NotImplementedError()


class DatabaseAuthenticationBackend(BaseAuthenticationBackend):
    def authenticate(self, username=None, password=None):
        from webtools.auth.models import User
        user = self.application.db.query(User)\
            .filter(User.username == username).one()
        return user
