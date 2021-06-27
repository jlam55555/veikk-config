from typing import Dict

from pyudev import Device

from veikk.evdev_util import EvdevUtil
from veikk.udev_util import UdevUtil
from veikk.veikk_device import VeikkDevice


class VeikkDaemon:

    def __init__(self):
        self._veikk_devices: Dict[str, VeikkDevice] = {}

        self._get_initial_veikk_devices()

        UdevUtil.init_udev_monitor(self._add_veikk_device,
                                   self._remove_veikk_device)

        # main thread sleeps forever sleep forever -- dbus loop?
        while True:
            input()

    def _get_initial_veikk_devices(self):
        for device in EvdevUtil.get_initial_devices():
            self._veikk_devices[device.path] = VeikkDevice(device)

    def _add_veikk_device(self, udev_device: Device):
        """
        Handler for udev add device event. If the device is an evdev device,
        add it to the dict of devices
        :param udev_device:
        :return:
        """
        if UdevUtil.is_veikk_evdev_device(udev_device):
            # TODO: need to protect self._veikk_devices with a mutex
            self._veikk_devices[UdevUtil.event_path(udev_device)] =\
                VeikkDevice(UdevUtil.to_evdev_device(udev_device))

    def _remove_veikk_device(self, udev_device: Device):
        """
        Handler for udev remove device event. If the device is an evdev device,
        remove it from the dict of devices.
        :param udev_device:
        :return:
        """
        if UdevUtil.is_veikk_evdev_device(udev_device):
            # TODO: same as above
            del self._veikk_devices[UdevUtil.event_path(udev_device)]
