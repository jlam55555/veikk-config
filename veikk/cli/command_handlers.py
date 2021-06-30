from ..common.evdev_util import EvdevUtil
from ..common.version import VEIKK_CONFIG_VERSION


class CommandHandlers:

    @staticmethod
    def show_devices(_):
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
    def show_version(_):
        """
        Show veikk-config version number.
        """
        print(VEIKK_CONFIG_VERSION)
