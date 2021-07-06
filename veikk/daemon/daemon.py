from typing import Dict
from evdev import InputDevice
from pyudev import Device

from veikk.daemon.dbus_loop import DbusLoop
from .event_loop import EventLoop
from .veikk_device import VeikkDevice
from ..common.evdev_util import EvdevUtil
from ..common.udev_util import UdevUtil
from ..common.veikk_config import VeikkConfig
from ..common.veikk_model import VeikkModel


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

        # get models data
        self._models_data = VeikkModel.get_models_data()

        # listen to udev, dbus, evdev events
        UdevUtil.init_udev_monitor(self._add_udev_veikk_device,
                                   self._remove_udev_veikk_device)
        self._dbus_loop = DbusLoop(self._config)
        self._event_loop = EventLoop()

        # initialize with initial set of devices; maps event path to device
        self._veikk_devices: Dict[str, VeikkDevice] = {}
        for device in EvdevUtil.get_initial_devices():
            self._add_veikk_device(device)

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
        self._veikk_devices[device.path] = VeikkDevice(device,
                                                       self._event_loop,
                                                       self._config,
                                                       self._models_data)

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
