from typing import Mapping
from evdev import InputDevice, UInput
from evdev import ecodes

from veikk._veikk_device import _VeikkDevice
from veikk.command.command import Command, KeyCode
from veikk.command.noop_command import NoopCommand
from veikk.event_loop import EventLoop

# no reason to have to create this multiple times, reuse this instance
noop = NoopCommand()


class VeikkDevice(_VeikkDevice):

    def __init__(self,
                 device: InputDevice,
                 event_loop: EventLoop,
                 command_map: Mapping[KeyCode, Command] = None) -> None:
        if command_map is None:
            command_map = {}

        self._device: InputDevice = device
        self._command_map = command_map

        # create a uinput device that has the properties of the original,
        # except the events
        self._uinput_device \
            = UInput.from_device(self._device,
                                 filtered_types=[ecodes.EV_SYN, ecodes.EV_KEY],
                                 name=f'Mapped {self._device.name}')

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
                self._command_map.get(event.code, noop)\
                    .execute(event, self._uinput_device)
        except OSError:
            self.cleanup()

    def cleanup(self) -> bool:
        """
        Perform any cleanup actions.
        :return:    True if this device has not been cleaned up before
        """
        if self._already_destroyed:
            return False

        try:
            self._event_loop.unregister_device(self)
            self._uinput_device.close()
        except OSError as err:
            print(err.strerror)

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
