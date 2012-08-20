
from sqlalchemy.orm.exc import NoResultFound

from .models import User
from .hashers import check_password

class BaseAuthenticationBackend(object):
    def __init__(self, application):
        self.application = application

    def authenticate(self, username=None, password=None):
        raise NotImplementedError()


class DatabaseAuthenticationBackend(BaseAuthenticationBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = self.application.db.query(User).filter(User.username == username).one()
            return user if check_password(password, user.password) else None
        except NoResultFound:
            return None
