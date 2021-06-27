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
        Converts a pyudev Device object to a evdev InputDevice object, if
        applicable. Since udev handles more devices than evdev devices, this
        will return None for other device types.
        :param device:  pyudev Device object
        :return:        evdev InputDevice object or None
        """
        return InputDevice(UdevUtil.event_path(device)) \
            if UdevUtil.is_udev_device(device) else None

    @staticmethod
    def is_udev_device(device: Device) -> bool:
        return device.sys_name.startswith('event')

    @staticmethod
    def event_path(device: Device) -> str:
        return f'/dev/input/{device.sys_name}'
