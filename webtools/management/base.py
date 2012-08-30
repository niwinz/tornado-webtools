import sys
import argparse
import importlib
import inspect
import logging
import logging.handlers
import os

from webtools.utils.imp import load_class

LOG = logging.getLogger(__name__)


class Command(object):
    def __init__(self, cmdapp, options):
        self.cmdapp = cmdapp
        self.options = options

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

    def get_parser(self):
        """
        Return an :class:`argparse.ArgumentParser`.
        """
        parser = argparse.ArgumentParser(
            description = self.get_description(),
            prog = self.get_name(),
        )
        return parser

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
        "webtools.management.commands.runserver.RunserverCommand"
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

    def find_command(self, argv):
        """
        Given an argument list, find a command and
        return the processor and any remaining arguments.
        """
        search_args = argv[:]
        name = ""

        commands = self._load_commands()

        while search_args:
            if search_args[0].startswith("-"):
                raise ValueError('Invalid command %r' % search_args[0])

            next_val = search_args.pop(0)
            name = '%s %s' % (name, next_val) if name else next_val
            if name in commands:
                cmd_cls = commands[name]
                return (cmd_cls, name, search_args)
        else:
            raise ValueError('Unknown command %r' %
                             (argv,))


class CommandApp(object):
    NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    LOG_FILE_MESSAGE_FORMAT = \
        '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'

    DEFAULT_VERBOSE_LEVEL = 1

    def __init__(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        description = "Webtools command manager"
        version = "0.1"

        self.parser = self.build_option_parser(description, version)
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
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        # Set up logging to a file
        if self.options.log_file:
            file_handler = logging.FileHandler(
                filename=self.options.log_file,
            )
            formatter = logging.Formatter(self.LOG_FILE_MESSAGE_FORMAT)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Always send higher-level messages to the console via stderr
        console = logging.StreamHandler(self.stderr)
        console_level = {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG,
        }.get(self.options.verbose_level, logging.DEBUG)
        console.setLevel(console_level)

        formatter = logging.Formatter(self.CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)

        root_logger.addHandler(console)

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
        try:
            self.options, remainder = self.parser.parse_known_args(argv)
            self.conf = self._load_settings(self.options.settings)
            self.configure_logging()
        except Exception as err:
            if hasattr(self, 'options'):
                debug = self.options.debug
            else:
                debug = True
            if debug:
                LOG.exception(err)
                raise
            else:
                LOG.error(err)
            return 1

        if len(argv) == 0:
            self.parser.print_help()
        else:
            return self.run_subcommand(remainder)

    def run_subcommand(self, argv):

        subcommand = self.manager.find_command(argv)
        cmd_cls, cmd_name, sub_argv = subcommand
        cmd = cmd_cls(self, self.options)

        result = 1
        try:
            cmd_parser = cmd.get_parser()
            parsed_args = cmd_parser.parse_args(sub_argv)
            result = cmd.run(parsed_args)
        except Exception as e:
            if self.options.debug:
                LOG.exception(e)
            else:
                LOG.error(e)
        finally:
            return result


def main(argv=sys.argv[1:]):
    app = CommandApp()
    return app.run(argv)
