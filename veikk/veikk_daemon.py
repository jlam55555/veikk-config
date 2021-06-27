from typing import Dict
from pyudev import Device

from veikk.evdev_util import EvdevUtil
from veikk.event_loop import EventLoop
from veikk.udev_util import UdevUtil
from veikk.veikk_device import VeikkDevice


class VeikkDaemon:
    """
    Entry point for veikk command. This is a singleton daemon and there should
    not be more than one instance of this created, or else unknown chaos (UB)
    will ensue.
    """

    def __init__(self):
        # event loop listens in the background forever
        self._event_loop = EventLoop()

        # maps a path to a device
        # initialize with initial set of devices
        self._veikk_devices: Dict[str, VeikkDevice] = {
            device.path: VeikkDevice(device, self._event_loop)
            for device in EvdevUtil.get_initial_devices()
        }

        # start listening for device add/remove events
        UdevUtil.init_udev_monitor(self._add_veikk_device,
                                   self._remove_veikk_device)

    def _add_veikk_device(self, udev_device: Device):
        """
        Handler for udev add device event. If the device is an evdev device,
        add it to the dict of devices
        :param udev_device:
        :return:
        """
        if UdevUtil.is_veikk_evdev_device(udev_device):
            # TODO: need to protect self._veikk_devices with a mutex
            self._veikk_devices[UdevUtil.event_path(udev_device)] = \
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
