from typing import List, Tuple
from evdev import UInput, ecodes, InputEvent

from veikk.command.command import Command, CommandType, KeyCode


class KeyComboCommand(Command):
    """
    Map a button or gesture to a key combination (or single key).
    """
    def __init__(self, keycodes: List[KeyCode]) -> None:
        self._keycodes = keycodes
        super(KeyComboCommand, self).__init__(CommandType.KEY_COMBO)

    @staticmethod
    def _is_btn_event(event_code) -> bool:
        """
        All (some?) button events are dispatched by the pen uinput device
        rather than the keyboard device. E.g., BTN_STYLUS won't work correctly
        if emitted on the keyboard device.

        See /include/uapi/linux/input-event-codes.h

        TODO: check that this is true of all BTN_* events

        :param event_code:  keyboard event to test
        :return:            whether this event should be fired on the pen
                            uinput device rather than the keyboard uinput device
        """
        return 0x100 <= event_code <= 0x151

    def execute(self,
                event: InputEvent,
                devices: Tuple[UInput, UInput]) -> None:
        """
        Dispatch keyboard characters.

        TODO: precalculate which device to use -- also shouldn't really mix
            devices

        :param event:       original input event -- used to detect whether
                            keydown or keyup (event.value)
        :param devices      virtual keyboard is devices[1]
        """
        for keycode in self._keycodes:
            devices[0 if KeyComboCommand._is_btn_event(keycode) else 1]\
                .write(ecodes.EV_KEY, keycode, event.value)
