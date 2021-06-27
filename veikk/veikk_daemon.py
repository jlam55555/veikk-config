from typing import Dict

from pyudev import Device

from veikk.evdev_util import EvdevUtil
from veikk.event_loop import EventLoop
from veikk.udev_util import UdevUtil
from veikk.veikk_device import VeikkDevice


class VeikkDaemon:

    def __init__(self):
        self._event_loop = EventLoop()

        # maps a path to a device
        self._veikk_devices: Dict[str, VeikkDevice] = {
            device.path: VeikkDevice(device, self._event_loop)
            for device in EvdevUtil.get_initial_devices()
        }

        UdevUtil.init_udev_monitor(self._add_veikk_device,
                                   self._remove_veikk_device)

        # main thread sleeps forever sleep forever -- dbus loop?
        # while True:
        #     input()

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
                VeikkDevice(UdevUtil.to_evdev_device(udev_device),
                            self._event_loop)

    def _remove_veikk_device(self, udev_device: Device):
        """
        Handler for udev remove device event. If the device is an evdev device,
        remove it from the dict of devices.
        :param udev_device:
        :return:
        """
        if UdevUtil.is_veikk_evdev_device(udev_device):
            # TODO: same as above
            if self._veikk_devices[UdevUtil.event_path(udev_device)].cleanup():
                del self._veikk_devices[UdevUtil.event_path(udev_device)]
