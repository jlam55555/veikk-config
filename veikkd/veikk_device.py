from typing import Mapping

from evdev import InputDevice, UInput, AbsInfo
from evdev import ecodes

from veikkd._veikk_device import _VeikkDevice
from veikkd.command.command import Command, KeyCode
from veikkd.command.noop_command import NoopCommand
from veikkd.evdev_util import EvdevUtil
from veikkd.event_loop import EventLoop

# no reason to have to create this multiple times, reuse this instance
noop = NoopCommand()


class VeikkDevice(_VeikkDevice):

    def __init__(self,
                 device: InputDevice,
                 event_loop: EventLoop,
                 command_map: Mapping[KeyCode, Command] = None) -> None:

        # TODO: remove; for testing
        # simple mapping for testing
        from evdev import ecodes
        from veikkd.command.program_command import ProgramCommand
        from veikkd.command.keycombo_command import KeyComboCommand
        from veikkd.command.command import CommandTriggerMap, CommandTrigger
        from veikkd.command.pentransform_command import PenTransformCommand
        pen_command = PenTransformCommand()
        command_map = {
            ecodes.ABS_X: pen_command,
            ecodes.ABS_Y: pen_command,
            ecodes.ABS_PRESSURE: pen_command,
            ecodes.BTN_TOUCH: KeyComboCommand([ecodes.BTN_TOUCH]),
            ecodes.BTN_STYLUS: KeyComboCommand([ecodes.BTN_STYLUS]),
            ecodes.BTN_STYLUS2: KeyComboCommand([ecodes.BTN_STYLUS2]),
            ecodes.BTN_0: ProgramCommand(['echo', 'Hello, world!', ';', 'read'],
                                         True),
            ecodes.BTN_1: ProgramCommand(['htop'], True,
                                         start_new_session=True),
            ecodes.BTN_2: KeyComboCommand([ecodes.KEY_LEFTCTRL,
                                           ecodes.KEY_RIGHTSHIFT,
                                           ecodes.KEY_E]),
            ecodes.BTN_3: ProgramCommand(['krita'],
                                         run_as_user='jon'),
            ecodes.BTN_4: ProgramCommand([
                'xvkbd', '-no-jump-pointer', '-text', 'Hello, world'],
                trigger_type_map=CommandTriggerMap(CommandTrigger.KEYUP)),

            # have to manually specify a user for this to work.
            ecodes.BTN_5: ProgramCommand(['google-chrome'],
                                         run_as_user='jon'),

            ecodes.BTN_6: KeyComboCommand([ecodes.KEY_VOLUMEUP]),
            ecodes.BTN_7: KeyComboCommand([ecodes.KEY_BACKSPACE]),

            ecodes.BTN_WEST: KeyComboCommand([ecodes.KEY_LEFTBRACE]),
            ecodes.BTN_EAST: KeyComboCommand([ecodes.KEY_RIGHTBRACE]),
            ecodes.BTN_NORTH: KeyComboCommand([ecodes.KEY_EQUAL]),
            ecodes.BTN_SOUTH: KeyComboCommand([ecodes.KEY_MINUS]),
            ecodes.BTN_TOOL_DOUBLETAP: KeyComboCommand([ecodes.KEY_LEFTCTRL,
                                                        ecodes.KEY_0])
        }

        if command_map is None:
            command_map = {}

        self._device: InputDevice = device
        self._command_map = command_map

        # remove the word " Bundled" from the device name
        self._device_name = device.name[:-8]

        self._uinput_devices = (self._setup_uinput_pen(),
                                self._setup_uinput_keyboard())

        # get exclusive access to device (i.e., the events will not get used
        # by the display server)
        self._device.grab()

        # the destroy method may be called from the udev event or when
        # the InputDevice::read() fails, whichever comes sooner
        self._already_destroyed = False

        if __debug__:
            print(f'New VeikkDevice: {self._device_name}')

        self._event_loop = event_loop
        self._event_loop.register_device(self)

    def _setup_uinput_pen(self) -> UInput:
        """
        Creates uinput device to dispatch pen (ABS_*, BTN_*) events on.

        TODO: get capabilities from the device

        :return:
        """
        capabilities = {
            ecodes.EV_KEY: EvdevUtil.get_pen_evkey_events(),
            ecodes.EV_ABS: [
                (ecodes.ABS_X, AbsInfo(value=0, min=0, max=50800,
                                       fuzz=0, flat=0, resolution=100)),
                (ecodes.ABS_Y, AbsInfo(value=0, min=0, max=30480,
                                       fuzz=0, flat=0, resolution=100)),
                (ecodes.ABS_PRESSURE, AbsInfo(value=0, min=0, max=8192,
                                              fuzz=0, flat=0,
                                              resolution=100))
            ]
        }
        input_props = [ecodes.INPUT_PROP_POINTER]
        return UInput(events=capabilities,
                      name=f'{self._device_name} Pen',
                      input_props=input_props)

    def _setup_uinput_keyboard(self) -> UInput:
        """
        Creates uinput device to dispatch keyboard events on. Allows any
        keyboard event, except those that only work when dispatched on a pen
        device (see EvdevUtil::is_pen_event).

        :return:    created uinput device
        """
        capabilities = {
            ecodes.EV_KEY: [code
                            for code, _ in ecodes.bytype[ecodes.EV_KEY].items()
                            if not EvdevUtil.is_pen_event(code)]
        }
        input_props = None
        return UInput(events=capabilities,
                      name=f'{self._device_name} Keyboard',
                      input_props=input_props)

    def handle_events(self) -> None:
        """
        Gets called when an event is emitted by the InputDevice. Is set up with
        pen/mouse and button capabilities.

        :return:
        """
        try:
            for event in self._device.read():
                # automatically send all sync events, regardless of mapping;
                # this is so to simplify the mappings
                if event.type == ecodes.EV_SYN:
                    self._uinput_devices[0].write_event(event)
                    self._uinput_devices[1].write_event(event)
                else:
                    self._command_map.get(event.code, noop) \
                        .execute(event, self._uinput_devices)
        except OSError:
            # device removed -- clean up normally
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
            self._uinput_devices[0].close()
            self._uinput_devices[1].close()
        except OSError as err:
            # sometimes occurs if device was not registered with the event loop
            print(f'Ignoring error: {err.strerror}')

        self._already_destroyed = True

        if __debug__:
            print(f'Disconnected VeikkDevice: {self._device_name}')

        return True

    def fileno(self) -> int:
        """
        Implement the HasFileno interface
        :return:    fd of the associated InputDevice
        """
        return self._device.fileno()
