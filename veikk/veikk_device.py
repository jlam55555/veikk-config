from evdev import InputDevice, InputEvent, categorize
from threading import Thread

from veikk._veikk_device import _VeikkDevice
from veikk.event_loop import EventLoop


class VeikkDevice(_VeikkDevice):

    def __init__(self, device: InputDevice, event_loop: EventLoop) -> None:
        self._device: InputDevice = device

        # get exclusive access to device (i.e., the events will not get used
        # by the display server)
        self._device.grab()

        self._already_destroyed = False

        if __debug__:
            print(f'New VeikkDevice: {self._device.name}')

        self._event_loop = event_loop
        self._event_loop.register_device(self)

    def handle_events(self) -> None:
        """
        Gets called when an event is emitted by the InputDevice.
        :return:
        """
        try:
            for event in self._device.read():
                print(categorize(event))
            print('event done')
        except OSError:
            self.cleanup()

    def cleanup(self):
        """
        Perform any cleanup actions. (Currently does nothing.)
        :return:
        """
        if self._already_destroyed:
            return

        self._event_loop.unregister_device(self)
        self._already_destroyed = True

        if __debug__:
            print(f'Disconnected VeikkDevice: {self._device.name}')

    def fileno(self) -> int:
        """
        Implement the HasFileno interface
        :return:    fd of the associated InputDevice
        """
        return self._device.fileno()
