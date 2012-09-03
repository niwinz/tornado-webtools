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

        from webtools.application import Application
        app = Application(self.cmdapp.conf)

        print("Create theese tables:")
        for tbl in Base.metadata.sorted_tables:
            print(" * {0}".format(tbl.name))

        res = input("Create [Y/n] ")
        if not res or res.lower() == "y":
            res = True
        else:
            res = False


        if res:
            Base.metadata.create_all(app.engine)
