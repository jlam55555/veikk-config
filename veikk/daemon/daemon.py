from typing import Dict
from evdev import InputDevice
from pyudev import Device

from .config_change_notifier import ConfigChangeNotifier
from .event_loop import EventLoop
from .veikk_device import VeikkDevice
from ..common.evdev_util import EvdevUtil
from ..common.udev_util import UdevUtil
from ..common.veikk_config import VeikkConfig


class Daemon:
    """
    Entry point for veikkd command. This is a singleton daemon and there should
    not be more than one instance of this created, or else unknown chaos (UB)
    will ensue.
    """

    def __init__(self, default_config: VeikkConfig = None):
        if default_config is None:
            default_config = {}
        self._config = default_config

        # event loop listens in the background forever
        self._event_loop = EventLoop()

        # initialize with initial set of devices; maps event path to device
        self._veikk_devices: Dict[str, VeikkDevice] = {}
        for device in EvdevUtil.get_initial_devices():
            self._add_veikk_device(device)

        # start listening for device add/remove events
        UdevUtil.init_udev_monitor(self._add_udev_veikk_device,
                                   self._remove_udev_veikk_device)

        # listen to changes
        # TODO: change this to use dbus?
        ConfigChangeNotifier('/tmp/veikk').listen_thread()

    def _add_udev_veikk_device(self, udev_device: Device):
        """
        Handler for udev add device event. If the device is an evdev device,
        add it to the dict of devices
        :param udev_device:
        :return:
        """
        if UdevUtil.is_veikk_evdev_device(udev_device):
            # TODO: need to protect self._veikk_devices with a mutex
            self._add_veikk_device(UdevUtil.to_evdev_device(udev_device))

    def _add_veikk_device(self, device: InputDevice):
        """
        Add veikk device from evdev device
        :param device:
        :return:
        """
        self._veikk_devices[device.path] \
            = VeikkDevice(device, self._event_loop, self._config)

    def _remove_udev_veikk_device(self, udev_device: Device):
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
