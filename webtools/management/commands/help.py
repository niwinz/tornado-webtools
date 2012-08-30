from webtools.management.base import Command

class HelpCommand(Command):
    """
    Show all available commands and these description.
    """

    def take_action(self, options):
        print("Available commands:")

        commands = self.cmdapp.manager._load_commands()
        for name, klass in commands.items():
            description = klass.get_description()
            if description:
                print("- {0}: {1}".format(name, description))
            else:
                print("- {0}".format(name))
