from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Any
import sys
import os
import yaml

from .command_handlers import CommandHandlers

# we need to import these classes even if unused in order to run the
# metaclass constructor, which registers the YAML constructors
from ..common.command.program_command import ProgramCommand
from ..common.command.keycombo_command import KeyComboCommand


class CliParser:
    """
    Entry point for the veikkctl CLI. Must be run as root (see _check_root()).
    """

    def __init__(self):
        """
        Entry point for CLI. Run the parser.
        """
        self._run_as_root()

        self._command_handlers = CommandHandlers()
        self._parse()

    def _create_parser(self,
                       schema: Dict,
                       parent: Any = None) -> ArgumentParser:
        """
        Creates a parser from the provided schema. See subcommands.yaml.

        (The type of parent is not exposed in the package, so the type
        annotation is Any.)

        :param schema:  dict of properties describing the current parser
        :param parent:  created by parent_parser.add_subparsers()
        :return:        the created parser (retval only used at the top level)
        """

        assert 'prog' in schema or parent is not None

        # create parser: top-level
        if parent is None:
            parser = ArgumentParser(prog=schema['prog'])

        # create parser: not top-level
        else:
            if 'aliases' not in schema:
                schema['aliases'] = [schema['name'][0]]
            parser = parent.add_parser(schema['name'],
                                       help=schema['help'],
                                       aliases=schema['aliases'])

        # create subcommands recursively
        if 'subcommands' in schema:
            subparsers = parser.add_subparsers(dest='subparser')
            for subcommand in schema['subcommands']:
                self._create_parser(subcommand, subparsers)

        # set any arguments
        if 'arguments' in schema:
            for argument_options in schema['arguments']:
                # get argument name and convert to array
                argument_name = argument_options['name']
                del argument_options['name']
                if not isinstance(argument_name, list):
                    argument_name = [argument_name]

                # if applicable, get argument type as string and convert to type
                if 'type' in argument_options:
                    argument_options['type'] = \
                        __builtins__[argument_options['type']]

                parser.add_argument(*argument_name, **argument_options)

        # set handler if applicable
        if 'func' in schema:
            parser.set_defaults(func=getattr(self._command_handlers,
                                             schema['func']))

        return parser

    def _parse(self) -> None:
        """
        Parse arguments using argparse. Uses subcommand syntax with single-
        character aliases for a nice CLI interface.

        :return:
        """
        with open(Path(__file__).parent / 'subcommands.yaml') as subcommands_fd:
            subcommands_yaml = subcommands_fd.read()

        subcommands_schema = yaml.safe_load(subcommands_yaml)
        parser = self._create_parser(subcommands_schema)
        args = parser.parse_args()
        args.func(args)

    @staticmethod
    def _run_as_root() -> None:
        """
        Promote to root at start if not already. Note that this won't work
        if this is ever turned into a GUI -- then we would (probably)
        need a polkit action. This way is simpler and doesn't require polkit.

        If already root, this is basically a no-op.

        TODO: change this to use polkit, since that will work with launching
            as a GUI as well

        Similar to https://stackoverflow.com/a/3819134, but uses exec syscall
        rather than subprocess
        """
        if os.geteuid() != 0:
            print('cli is dangerous and must be run as root!\n'
                  'Promoting to root...')
            os.execvp('sudo', ['-E', sys.executable] + sys.argv)
