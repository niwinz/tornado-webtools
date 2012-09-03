from webtools.management.base import Command
from webtools.database import Base

class ShellCommand(Command):
    """
    Syncronize all available sqlalchemy defined tables
    to a database server.
    """

    def take_action(self, options):
        if not options.settings:
            raise RuntimeError("For start serverm --settings parameter"
                                " is mandatory!")

        from webtools.application import Application
        app = Application(self.cmdapp.conf)

        imported_objects = {'app': app}

        import code

        try:
            import readline
        except ImportError:
            pass
        else:
            import rlcompleter
            readline.set_completer(rlcompleter.Completer(imported_objects).complete)
            readline.parse_and_bind("tab:complete")

        code.interact(local=imported_objects)
