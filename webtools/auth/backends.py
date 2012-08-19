class BaseHandler(object):
    def authenticate(self, username=None, password=None):
        raise NotImplementedError()

    def get_user(self, pk):
        raise NotImplementedError()
