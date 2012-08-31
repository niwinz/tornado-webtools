from webtools.management.base import Command
from webtools.utils.imp import load_class
from webtools.database import Base

from importlib import import_module


class SyncdbCommand(Command):
    """
    Syncronize all available sqlalchemy defined tables
    to a database server.
    """

    def take_action(self, options):
        if not options.settings:
            raise RuntimeError("For start serverm --settings parameter"
                                " is mandatory!")
        try:
            settings_cls = load_class(options.settings)
        except ImportError:
            raise RuntimeError("Cannot load settings class: {0}".format(options.settings))

        conf = settings_cls()

        models_modules = conf.MODELS_MODULES or []
        assert isinstance(models_modules, (list, tuple)), "MODELS_MODULES must be a list or tuple"

        for module_path in set(models_modules):
            try:
                import_module(module_path)
            except ImportError:
                continue

        from webtools.application import Application
        app = Application(conf)

        print("Creating tables...")
        Base.metadata.create_all(app.engine)
