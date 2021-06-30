from ..common.evdev_util import EvdevUtil
from ..common.version import VEIKK_CONFIG_VERSION


class CommandHandlers:

    @staticmethod
    def show_devices(_):
        """
        List all connected VEIKK devices
        :param _:
        :return:
        """
        print('Current VEIKK devices:')
        print('\n'.join(['- ' + device.name[:-7]
                         for device in EvdevUtil.get_initial_devices()
                         if device.name.endswith('Bundled')]))

    @staticmethod
    def show_version(_):
        """
        Show version number

        TODO: get this from somewhere else
        :param _:
        :return:
        """
        print(VEIKK_CONFIG_VERSION)
