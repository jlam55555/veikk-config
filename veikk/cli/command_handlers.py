import subprocess
from os import environ
from pydbus import SystemBus

from veikk.common.constants import VEIKK_DBUS_OBJECT, VEIKK_DBUS_INTERFACE
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
    def edit_config(_) -> None:
        """
        Edit configuration file. Try to use default editor, if set
        in the EDITOR environment variable.

        TODO: the sudo promotion in _run_as_root() doesn't work well to
            preserve environment variables, so this may not end up using
            the user's $EDITOR envvar

        :param _:
        :return:
        """
        if environ.get('EDITOR') is not None:
            subprocess.run([environ.get('EDITOR'),
                            constants.VEIKK_CONFIG_LOCATION])
        else:
            # use nano as a default editor, will probably exist
            subprocess.run(['xterm', '-e', '/usr/bin/nano',
                            constants.VEIKK_CONFIG_LOCATION])

    def get_config(self, _) -> None:
        """
        Get the current configuration.
        """
        print(self._dbus_object.GetCurrentConfig(0))

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
        print('Current VEIKK devices:')
        print('\n'.join(['- ' + device.name[:-7]
                         for device in EvdevUtil.get_initial_devices()
                         if device.name.endswith('Bundled')]))

    @staticmethod
    def show_version(_) -> None:
        """
        Show veikk-config version number.
        """
        print(constants.VEIKK_CONFIG_VERSION)
