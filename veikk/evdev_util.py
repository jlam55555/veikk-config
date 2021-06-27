from evdev import InputDevice, list_devices
from typing import List


class EvdevUtil:
    """
    Static utility functions for evdev
    """

    @staticmethod
    def get_initial_devices() -> List[InputDevice]:
        """
        Gets the list of VEIKK devices at boot
        :return:    list of current VEIKK devices
        """
        return list(filter(EvdevUtil._is_veikk_device,
                           [InputDevice(path) for path in list_devices()]))

    @staticmethod
    def _is_veikk_device(device: InputDevice) -> bool:
        """
        Determines whether a evdev device is a VEIKK device
        :param device:  evdev device
        :return:        whether evdev device is a VEIKK device
        """
        return device.name.startswith("VEIKK ")
