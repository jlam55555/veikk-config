from selectors import DefaultSelector, EVENT_READ
from threading import Thread

from ._veikk_device import _VeikkDevice


class EventLoop:
    """
    EventLoop listens to evdev events and runs the associated commands. Runs
    in a separate thread.
    """

    def __init__(self):
        self._selector = DefaultSelector()
        Thread(target=self._event_loop_thread).start()

    def register_device(self, device: _VeikkDevice):
        """
        Register device with the selector
        :param device:
        :return:
        """
        self._selector.register(device, EVENT_READ)

    def unregister_device(self, device: _VeikkDevice):
        """
        Unregister device from selector
        :param device:
        :return:
        """

        # in some rare cases, the device may not get registered (e.g., inserting
        # and removing the device quickly, so wrap this in a try/except block
        try:
            self._selector.unregister(device)
        except KeyError:
            if __debug__:
                print(f'Keyerror on unregistering {device.fileno()}')

    def _event_loop_thread(self):
        """
        Main evdev mapping event loop
        """
        # TODO: self._selector should also probably be protected with an mutex
        while True:
            for key, _ in self._selector.select():
                assert isinstance(key.fileobj, _VeikkDevice)    # type guard
                key.fileobj.handle_events()
