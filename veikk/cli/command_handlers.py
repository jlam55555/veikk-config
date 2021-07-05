import subprocess
from argparse import Namespace
from os import environ
from pydbus import SystemBus

from veikk.common.constants import VEIKK_DBUS_OBJECT, VEIKK_DBUS_INTERFACE
from veikk.common.veikk_config import VeikkConfig
from veikk.common.veikk_daemon_dbus import VeikkDaemonDbus
from ..common.evdev_util import EvdevUtil
from ..common import constants


class CommandHandlers:
    """
    Handle commands emitted from running the
    """

    def __init__(self):
        self._dbus_object: VeikkDaemonDbus \
            = SystemBus().get(VEIKK_DBUS_OBJECT, VEIKK_DBUS_INTERFACE)

    @staticmethod
    def _format_config(input_str: str) -> str:
        """
        Formats YAML text differently so that it is easily identifiable.
        :param input_str:   string to format
        :return             formatted string.
        """
        return f'\n##### begin YAML\n\n{input_str}\n##### end YAML\n'

    @staticmethod
    def edit_config(_) -> None:
        """
        Edit configuration file. Try to use default editor, if set
        in the EDITOR environment variable.

        TODO: the sudo promotion in _run_as_root() doesn't work well to
            preserve environment variables, so this may not end up using
            the user's $EDITOR envvar

        :param _:
        """
        if environ.get('EDITOR') is not None:
            subprocess.run([environ.get('EDITOR'),
                            constants.VEIKK_CONFIG_LOCATION])
        else:
            # use nano as a default editor, will probably exist
            subprocess.run(['xterm', '-e', '/usr/bin/nano',
                            constants.VEIKK_CONFIG_LOCATION])

    def get_config(self, args: Namespace) -> None:
        """
        Get the current configuration.
        :param args:
        """
        config_yaml = self._dbus_object.GetCurrentConfig(0)
        config = VeikkConfig.load_yaml(config_yaml)

        sp = args.subparser
        if sp == 'button' or sp == 'b':
            print(f'Current button mapping for {args.keycode}:')
            print(self._format_config(
                config.get_button_command(args.keycode).dump_yaml()))
        elif sp == 'pen' or sp == 'p':
            print('Current pen transform:')
            print(self._format_config(config.get_pen_command().dump_yaml()))
        else:
            print('Current configuration:')
            print(self._format_config(config_yaml))

    def apply_config(self, _) -> None:
        """
        Apply the settings in the conf file to the daemon.
        """
        self._dbus_object.LoadConfigFromFile(0, '')

    def save_config(self, _) -> None:
        """
        Save the settings from the daemon to the conf file
        """
        self._dbus_object.SaveConfigToFile(0, '')

    @staticmethod
    def show_devices(_) -> None:
        """
        List all connected VEIKK devices. Each device created by the driver
        will end in the word "Bundled". (Additional evdev devices created by
        the mapping daemon will end in "Pen" or "Keyboard".)
        """
        veikk_devices = ['- ' + device.name[:-7]
                         for device in EvdevUtil.get_initial_devices()
                         if device.name.endswith('Bundled')]
        if len(veikk_devices) > 0:
            print('Current VEIKK devices:' + '\n'.join(veikk_devices))
        else:
            print('No connected VEIKK devices found.')

    @staticmethod
    def show_version(_) -> None:
        """
        Show veikk-config version number.
        """
        print(constants.VEIKK_CONFIG_VERSION)
