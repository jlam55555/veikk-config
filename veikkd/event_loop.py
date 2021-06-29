from selectors import DefaultSelector, EVENT_READ
from threading import Thread

from veikkd._veikk_device import _VeikkDevice


class EventLoop:
    def __init__(self):
        self._selector = DefaultSelector()
        Thread(target=self._event_loop_thread).start()

    def register_device(self, device: _VeikkDevice):
        self._selector.register(device, EVENT_READ)

    def unregister_device(self, device: _VeikkDevice):
        # in some rare cases, the device may not get registered (e.g., inserting
        # and removing the device quickly, so wrap this in a try/except block
        try:
            self._selector.unregister(device)
        except KeyError:
            if __debug__:
                print(f'Keyerror on unregistering {device.fileno()}')

    def _event_loop_thread(self):
        # TODO: self._selector should also probably be protected with an mutex
        while True:
            for key, _ in self._selector.select():
                # kill the typing hint in the following line
                assert isinstance(key.fileobj, _VeikkDevice)
                key.fileobj.handle_events()
