import sys
import argparse
import traceback
import importlib
import inspect
import logging
import logging.handlers
import os

from webtools.utils.imp import load_class

LOG = logging.getLogger(__name__)


class Command(object):
    def __init__(self, cmdapp):
        self.cmdapp = cmdapp

    @classmethod
    def get_name(cls):
        name = cls.__name__.lower()
        if name.endswith("command"):
            name = name[:-7]
        elif name.endswith("cmd"):
            name = name[:-3]
        return name

    @classmethod
    def get_description(cls):
        doc = inspect.getdoc(cls)
        if not doc:
            return ""

        return doc.strip().split("\n")[0]

    @classmethod
    def get_parser(cls, root_parser):
        """
        Return an :class:`argparse.ArgumentParser`.
        """
        return root_parser

    def take_action(self, parsed_args):
        """
        Override to do something useful.
        """
        raise NotImplementedError

    def run(self, parsed_args):
        """
        Invoked by the application when the command is run.

        Developers implementing commands should override
        :meth:`take_action`.

        Developers creating new command base classes (such as
        :class:`Lister` and :class:`ShowOne`) should override this
        method to wrap :meth:`take_action`.
        """
        self.take_action(parsed_args)
        return 0


class CommandManager(object):
    commands = {}
    default_commands= [
        "webtools.management.commands.help.HelpCommand",
        "webtools.management.commands.runserver.RunserverCommand",
        "webtools.management.commands.syncdb.SyncdbCommand",
    ]

    def __init__(self, app):
        self.app = app

    def _load_commands(self):
        commands = {}

        command_list = set(self.default_commands[:])
        if self.app.conf is not None:
            command_list.update(self.app.conf.COMMANDS or [])

        for class_path in command_list:
            klass = load_class(class_path)
            commands[klass.get_name()] = klass

        return commands

    def find_command(self, name):
        """
        Given an argument list, find a command and
        return the processor and any remaining arguments.
        """

        commands = self._load_commands()
        if name in commands:
            return commands[name]

        return None


class CommandApp(object):
    NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'

    DEFAULT_VERBOSE_LEVEL = 2

    def __init__(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        description = "Webtools command manager"
        version = "0.1"

        self.root_parser = self.build_option_parser(description, version)
        self.manager = CommandManager(self)

    def build_option_parser(self, description, version):
        """
        Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        """
        parser = argparse.ArgumentParser(
            description=description
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
        )
        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )
        parser.add_argument(
            '--settings',
            action='store',
            default=None,
            help='Specify a settings class path.',
            dest="settings",
        )
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='suppress output except warnings and errors',
        )
        #parser.add_argument(
        #    '-h', '--help',
        #    action=HelpAction,
        #    nargs=0,
        #    default=self,  # tricky
        #    help="show this help message and exit",
        #)
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='show tracebacks on errors',
        )
        return parser

    def configure_logging(self):
        """
        Create logging handlers for any log output.
        """
        self.root_logger = logging.getLogger('')
        self.root_logger.setLevel(logging.DEBUG)

        # Always send higher-level messages to the console via stderr
        self.console = logging.StreamHandler(self.stderr)
        self.console.setLevel(logging.DEBUG)

        formatter = logging.Formatter(self.CONSOLE_MESSAGE_FORMAT)

        self.console.setFormatter(formatter)
        self.root_logger.addHandler(self.console)

    def _adjunst_logging_level(self, options):
        # Set up logging to a file
        if options.log_file:
            file_handler = logging.FileHandler(
                filename=options.log_file,
            )
            formatter = logging.Formatter(self.LOG_FILE_MESSAGE_FORMAT)
            file_handler.setFormatter(formatter)
            self.root_logger.addHandler(file_handler)

        console_level = {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG,
        }.get(options.verbose_level, logging.DEBUG)
        self.console.setLevel(console_level)

    def _load_settings(self, settings_path):
        """
        Load a main tornado application.
        """

        if settings_path is None:
            return None

        try:
            settings_cls = load_class(settings_path)
            return settings_cls()
        except ImportError:
            raise RuntimeError("Cannot import settings: {0}".format(settings_path))

    def run(self, argv):
        """
        Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        sys.path.insert(0, os.path.abspath("."))
        self.configure_logging()

        if len(argv) == 0:
            self.root_parser.print_help()
            return 1

        options, extra_args = self.root_parser.parse_known_args(argv)
        self.conf = self._load_settings(options.settings)
        self._adjunst_logging_level(options)

        if not argv[0].startswith("-"):
            command_name, argv = argv[0], argv[1:]

            cmd_cls = self.manager.find_command(command_name)
            if cmd_cls is None:
                raise RuntimeError("Command {0} not found".format(command_name))

            parser = cmd_cls.get_parser(self.root_parser)
            options = parser.parse_args(argv)
            return cmd_cls(self).run(options)

        return 1


def main(argv=sys.argv[1:]):
    app = CommandApp()
    return app.run(argv)
