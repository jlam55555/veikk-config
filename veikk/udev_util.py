# https://pyudev.readthedocs.io/en/latest/api/pyudev.glib.html#pyudev.glib.MonitorObserver
from typing import Callable

from evdev import InputDevice
from pyudev import Context, Monitor, MonitorObserver, Device

DeviceCallback = Callable[[Device], None]


class UdevUtil:
    """
    Static utility functions for udev
    """

    @staticmethod
    def init_udev_monitor(add_callback: DeviceCallback,
                          remove_callback: DeviceCallback) -> None:
        """
        Listen to udev events to automatically subscribe to new VEIKK devices
        being plugged in
        :return:    None
        """
        context = Context()
        monitor = Monitor.from_netlink(context)
        monitor.filter_by(subsystem='input')

        def callback(action: str, device: Device) -> None:
            if action == 'add':
                add_callback(device)
            elif action == 'remove':
                remove_callback(device)

        MonitorObserver(monitor, callback).start()

    @staticmethod
    def to_evdev_device(device: Device) -> InputDevice:
        """
        Converts a pyudev Device object to a evdev InputDevice object
        :param device:  pyudev Device object for a VEIKK device
        :return:        evdev InputDevice object
        """
        return InputDevice(UdevUtil.event_path(device))

    @staticmethod
    def is_veikk_evdev_device(device: Device) -> bool:
        """
        Since pyudev handles more than just evdev devices (there are the
        underlying devices as well) and not just VEIKK devices, we have to
        filter only the devices we want.
        :param device:  Device object
        :return:        whether the device is a VEIKK evdev device
        """
        return device.sys_name.startswith('event') and \
               device.properties['ID_VENDOR'] == 'VEIKK.INC'

    @staticmethod
    def event_path(device: Device) -> str:
        """
        Get the path needed to construct an evdev InputDevice.
        :param device:  Device object
        :return:        device event device path
        """
        return f'/dev/input/{device.sys_name}'
