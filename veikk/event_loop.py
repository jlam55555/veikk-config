from selectors import DefaultSelector, EVENT_READ
from threading import Thread

from veikk._veikk_device import _VeikkDevice


class EventLoop:
    def __init__(self):
        self._selector = DefaultSelector()
        Thread(target=self._event_loop_thread).start()

    def register_device(self, device: _VeikkDevice):
        self._selector.register(device, EVENT_READ)

    def unregister_device(self, device: _VeikkDevice):
        print(f'Attempting to unregister {device.fileno()}')
        self._selector.unregister(device)

    def _event_loop_thread(self):
        # TODO: self._selector should also probably be protected with an mutex
        while True:
            for key, _ in self._selector.select():
                # kill the typing hint in the following line
                assert isinstance(key.fileobj, _VeikkDevice)

                device = key.fileobj
                device.handle_events()
