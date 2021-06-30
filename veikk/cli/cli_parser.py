from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Any
import sys
import os
import yaml

# try to use LibYAML if present, use python implementation as fallback
# see: https://pyyaml.org/wiki/PyYAMLDocumentation
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .command_handlers import CommandHandlers


class CliParser:
    """
    Entry point for the veikkctl CLI. Must be run as root (see _check_root()).
    """

    def __init__(self):
        """
        Entry point for CLI. Run the parser.
        """
        self._run_as_root()
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
        if 'prog' in schema:
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
            subparsers = parser.add_subparsers()
            for subcommand in schema['subcommands']:
                self._create_parser(subcommand, subparsers)

        # create function (if this is a (possibly) terminal (sub)command)
        if 'func' in schema:
            def handler(args):
                getattr(CommandHandlers, schema['func'])(args)
            parser.set_defaults(func=handler)

        return parser

    def _parse(self):
        """
        Parse arguments using argparse. Uses subcommand syntax with single-
        character aliases for a nice CLI interface.

        :return:
        """
        with open(Path(__file__).parent / 'subcommands.yaml') as subcommands_fd:
            subcommands_yaml = subcommands_fd.read()

        subcommands_schema = yaml.load(subcommands_yaml, Loader=Loader)
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
