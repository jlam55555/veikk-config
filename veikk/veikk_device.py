from evdev import InputDevice, categorize

from veikk._veikk_device import _VeikkDevice
from veikk.event_loop import EventLoop


class VeikkDevice(_VeikkDevice):

    def __init__(self, device: InputDevice, event_loop: EventLoop) -> None:
        self._device: InputDevice = device

        # get exclusive access to device (i.e., the events will not get used
        # by the display server)
        self._device.grab()

        # the destroy method may be called from the udev event or when
        # the InputDevice::read() fails, whichever comes sooner
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

    def cleanup(self) -> bool:
        """
        Perform any cleanup actions.
        :return:    True if this device has not been cleaned up before
        """
        if self._already_destroyed:
            return False

        self._event_loop.unregister_device(self)
        self._already_destroyed = True

        if __debug__:
            print(f'Disconnected VeikkDevice: {self._device.name}')

        return True

    def fileno(self) -> int:
        """
        Implement the HasFileno interface
        :return:    fd of the associated InputDevice
        """
        return self._device.fileno()
