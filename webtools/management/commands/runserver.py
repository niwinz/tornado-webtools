
from webtools.management.base import Command
from webtools.utils.imp import load_class


class RunserverCommand(Command):
    def take_action(self, options):
        if not options.settings:
            raise RuntimeError("For start serverm --settings parameter"
                                " is mandatory!")
        try:
            settings_cls = load_class(options.settings)
        except ImportError:
            raise RuntimeError("Cannot load settings class: {0}".format(options.settings))

        from webtools.application import Application
        app = Application(settings_cls())
        app.listen(8888) # TODO: parametrize this

        import tornado.ioloop
        print("Listeing on :{0}".format(8888))
        tornado.ioloop.IOLoop.instance().start()
