from webtools.management.base import Command
from webtools.database import Base


class SyncdbCommand(Command):
    """
    Syncronize all available sqlalchemy defined tables
    to a database server.
    """

    def take_action(self, options):
        if not self.cmdapp.conf:
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


class DropdbCommand(Command):
    """
    Remove all tables.
    """

    def take_action(self, options):
        if not self.cmdapp.conf:
            raise RuntimeError("For start serverm --settings parameter"
                                " is mandatory!")

        from webtools.application import Application
        app = Application(self.cmdapp.conf)

        print("Drop theese tables:")
        for tbl in Base.metadata.sorted_tables:
            print(" * {0}".format(tbl.name))

        res = input("Drop [Y/n] ")
        if not res or res.lower() == "y":
            res = True
        else:
            res = False

        if res:
            Base.metadata.drop_all(app.engine)
