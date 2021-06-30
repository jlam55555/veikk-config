from typing import List, Tuple
from evdev import UInput, ecodes, InputEvent

from .command import Command, CommandType, KeyCode
from ..evdev_util import EvdevUtil


class KeyComboCommand(Command):
    """
    Map a button or gesture to a key combination (or single key).
    """
    def __init__(self, keycodes: List[KeyCode]) -> None:
        self._keycodes = keycodes
        super(KeyComboCommand, self).__init__(CommandType.KEY_COMBO)

    def execute(self,
                event: InputEvent,
                devices: Tuple[UInput, UInput]) -> None:
        """
        Dispatch keyboard characters.

        :param event:       original input event -- used to detect whether
                            keydown or keyup (event.value)
        :param devices      virtual pen is devices[0], keyboard is devices[1]
        """
        for keycode in self._keycodes:
            devices[0 if EvdevUtil.is_pen_event(keycode) else 1]\
                .write(ecodes.EV_KEY, keycode, event.value)
