import sys
import argparse
import inspect
import logging
import logging.handlers
import os

from webtools.utils.imp import load_class

LOG = logging.getLogger(__name__)


class Command(object):
    def get_name(self):
        name = self.__class__.__name__.lower()
        if name.endswith("command"):
            name = name[:-7]
        elif name.endswith("cmd"):
            name = name[:-3]
        return name

    def get_description(self):
        return inspect.getdoc(self.__class__) or ''

    def get_parser(self):
        """Return an :class:`argparse.ArgumentParser`.
        """
        parser = argparse.ArgumentParser(
            description = self.get_description(),
            prog = self.get_name(),
        )
        return parser

    def take_action(self, parsed_args):
        """Override to do something useful.
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
        "webtools.management.commands.help.HelpCommand"
    ]

    def __init__(self, app):
        self.app = app
        self._load_commands()

    def _load_commands(self):
        commands_to_load = set(self.app.conf.COMMANDS or [])
        commands_to_load.update(self.default_commands)

        for class_path from commands_to_load:
            klass = load_class(class_path)
            self.commands[klass.get_name()] = klass

    def find_command(self, argv):
        """
        Given an argument list, find a command and
        return the processor and any remaining arguments.
        """
        search_args = argv[:]
        name = ""

        while search_args:
            if search_args[0].startswith("-"):
                raise ValueError('Invalid command %r' % search_args[0])

            next_val = search_args.pop(0)
            name = '%s %s' % (name, next_val) if name else next_val
            if name in self.commands:
                cmd_cls = self.commands[name]
                return (cmd_cls, name, search_args)
        else:
            raise ValueError('Unknown command %r' %
                             (argv,))


class CommandApp(object):
    _app_loaded = False

    app_file = "app"
    app_callable = "application"

    def __init__(self):
        #self._load_main_app()
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

        self.manager = CommandManager(self)

        description = "Webtools command manager"
        version = "0.1"

        self.parser = self.build_option_parser(description, version)

    def _load_main_app(self):
        """
        Load a main tornado application.
        """

        if self._app_loaded:
            return

        _absolute_path = os.path.abspath(".")
        _module = importlib.import_module(self.app_file)

        self.application = getattr(_module, self.app_callable, None)

        if application is None:
            raise RuntimeError("Cannot load {0} from {1} module"\
                .format(self.app_callable, self.app_file))

        self.conf = self.application.conf
        self._app_loaded = True

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
            description=description,
            add_help=False,
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
        console_level = {0: logging.WARNING,
                         1: logging.INFO,
                         2: logging.DEBUG,
                         }.get(self.options.verbose_level, logging.DEBUG)
        console.setLevel(console_level)
        formatter = logging.Formatter(self.CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)
        return

    def run(self, argv):
        """
        Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            self.options, remainder = self.parser.parse_known_args(argv)
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
        return self.run_subcommand(remainder)

    def run_subcommand(self, argv):
        subcommand = self.manager.find_command(argv)
        cmd_cls, cmd_name, sub_argv = subcommand

        result = 1
        try:
            cmd_parser = cmd.get_parser()
            parsed_args = cmd_parser.parsed_args(sub_argv)
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
