from typing import List
from evdev import UInput, ecodes, InputEvent

from veikk.command.command import Command, CommandType

KeyCode = int


class KeyComboCommand(Command):
    def __init__(self, uinput_dev: UInput, keycodes: List[KeyCode]) -> None:
        self._keycodes = keycodes
        self._device = uinput_dev
        super(KeyComboCommand, self).__init__(CommandType.KEYCOMBO)

    def execute(self, event: InputEvent) -> None:
        for keycode in self._keycodes:
            self._device.write(ecodes.EV_KEY, keycode, event.value)
        self._device.syn()
