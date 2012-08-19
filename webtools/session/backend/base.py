import uuid

class BaseSessionEngine(object):
    def __init__(self, application):
        self._application = application
        self._session_data = None
        self._modified = False
        self._current_session_key = None

    @property
    def is_modified(self):
        return self._modified

    @property
    def session_key(self):
        return self._application.settings.get('session_key', 'tornado_webtools_sessionid')

    def __contains__(self, key):
        return key in self.session_data

    def __getitem__(self, key):
        return self.session_data[key]

    def __setitem__(self, key, value):
        self.session_data[key] = value
        self._modified = True

    def __delitem__(self, key):
        del self.session_data[key]
        self._modified = True

    def get(self, key, default=None):
        return self.session_data.get(key, default)

    def pop(self, key, *args):
        self._modified = self._modified or key in self.session_data
        return self.session_data.pop(key, *args)

    def update(self, data):
        assert isinstance(data, dict), "the first parameter must be a dict instance"
        self.session_data.update(data)
        self._modified = True

    def keys(self):
        return self.session_data.keys()

    def values(self):
        return self.session_data.values()

    def items(self):
        return self.session_data.items()

    def clear(self):
        self._session_data = {}
        self._modified = True

    def random_session_key(self):
        return str(uuid.uuid1())

    @property
    def session_key(self):
        return self._current_session_key

    def flush(self):
        self.clear()
        self.delete()

    @property
    def session_data(self):
        if self._session_data is None:
            self.load()

        return self._session_data

    def load(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()
