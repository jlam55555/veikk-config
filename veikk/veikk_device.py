from evdev import InputDevice, InputEvent
from threading import Thread


class VeikkDevice:

    def __init__(self, device: InputDevice) -> None:
        self._device: InputDevice = device

        if __debug__:
            print(f'New VeikkDevice: {self._device.name}')

        Thread(target=self._event_loop_thread).start()

    def _event_loop_thread(self) -> None:
        try:
            for event in self._device.read_loop():
                self._handle_event(event)
        except OSError:
            self._cleanup()

    def _handle_event(self, event: InputEvent) -> None:
        print(event)

    def _cleanup(self):
        if __debug__:
            print(f'Disconnected VeikkDevice: {self._device.name}')