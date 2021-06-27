from typing import List
from evdev import UInput, ecodes, InputEvent

from veikk.command.command import Command, CommandType, KeyCode


class KeyComboCommand(Command):
    """
    Map a button or gesture to a key combination (or single key).
    """
    def __init__(self, keycodes: List[KeyCode]) -> None:
        self._keycodes = keycodes
        super(KeyComboCommand, self).__init__(CommandType.KEYCOMBO)

    def execute(self, event: InputEvent, device: UInput) -> None:
        """
        Dispatch keyboard characters.
        :param event:       original input event -- used to detect whether
                            keydown or keyup (event.value)
        :param device       virtual device to emit event on
        """
        if event.type == ecodes.EV_SYN:
            device.write(event)
        else:
            for keycode in self._keycodes:
                device.write(ecodes.EV_KEY, keycode, event.value)
