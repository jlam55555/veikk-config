from typing import List, Tuple, Dict, Union
from evdev import UInput, ecodes, InputEvent

from .command import Command, CommandType, KeyCode
from ..evdev_util import EvdevUtil


class KeyComboCommand(Command):
    """
    Map a button or gesture to a key combination (or single key).
    """
    def __init__(self, keycodes: List[Union[str, KeyCode]]) -> None:
        # convert any string keycodes to keycodes (numbers)
        for i, key in enumerate(keycodes):
            if isinstance(key, str):
                keycodes[i] = EvdevUtil.str_to_keycode(key)

        self._keycodes = keycodes
        super(KeyComboCommand, self).__init__(CommandType.KEY_COMBO)

    def _verify(self) -> None:
        """
        Perform any necessary checks.

        TODO: what checks should be performed?
        """
        pass

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

    def _to_yaml_dict(self) -> Dict:
        return {
            "keycodes": list(map(EvdevUtil.keycode_to_str, self._keycodes))
        }
