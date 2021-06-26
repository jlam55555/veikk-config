# https://pyudev.readthedocs.io/en/latest/api/pyudev.glib.html#pyudev.glib.MonitorObserver

from pyudev import Context, Monitor


class UdevManager:

    @staticmethod
    def init_udev_monitor():
        context = Context()
        monitor = Monitor.from_netlink(context)
        monitor.filter_by(subsystem='input')

        for action, device in monitor:
            print(f'Monitor: {action}: {device}')
