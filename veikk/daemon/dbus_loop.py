from threading import Thread

from pydbus import SystemBus
from gi.repository import GLib

from ..common.constants import VEIKK_DBUS_OBJECT
from ..common.veikk_daemon_dbus import VeikkDaemonDbus
from ..common.veikk_config import VeikkConfig


class DbusLoop:
    """
    Creates the dbus interface/object and listens to changes. Runs in a
    separate thread.
    """

    def __init__(self, config: VeikkConfig):
        self._config = config
        self._dbus_object = VeikkDaemonDbus(self._config)

        # publish object on dbus
        bus = SystemBus()
        bus.publish(VEIKK_DBUS_OBJECT, self._dbus_object)

        # use glib's mainloop (default for glib)
        self._event_loop = GLib.MainLoop()

        # run glib's mainloop in separate thread
        Thread(target=self._event_loop.run).start()
