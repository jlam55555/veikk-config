import subprocess
from os import environ

from ..common.evdev_util import EvdevUtil
from ..common import constants


class CommandHandlers:

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

    @staticmethod
    def apply_config(_) -> None:
        """
        TODO: implement this with dbus
        """
        pass

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
