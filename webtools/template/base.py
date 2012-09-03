class Library(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Library, self).__new__(*args, **kwargs)
        return cls._instance

    def __init__(self):
        self._globals = {}
        self._tests = {}
        self._filters = {}

    def _update_env(self, env):
        env.filters.update(self._filters)
        env.globals.update(self._globals)
        env.tests.update(self._tests)

    def _new_function(self, attr, func, name=None):
        _attr = getattr(self, attr)
        if name is None:
            name = func.__name__

        _attr[name] = func
        return func

    def _function(self, attr, name=None, _function=None):
        if name is None and _function is None:
            def dec(func):
                return self._new_function(attr, func)
            return dec

        elif name is not None and _function is None:
            if callable(name):
                return self._new_function(attr, name)

            else:
                def dec(func):
                    return self._function(attr, name, func)
                return dec

        elif name is not None and _function is not None:
            return self._new_function(attr, _function, name)

        raise RuntimeError("Invalid parameters")

    def global(self, *args, **kwargs):
        return self._function("_globals", *args, **kwargs)

    def test(self, *args, **kwargs):
        return self._function("_tests", *args, **kwargs)

    def filter(self, *args, **kwargs):
        return self._function("_filters", *args, **kwargs)
