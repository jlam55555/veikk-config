from typing import Dict, Tuple, Union
from evdev import ecodes, InputEvent, UInput

from .command.command import KeyCode, Command
from .command.noop_command import NoopCommand
from .command.pentransform_command import PenTransformCommand
from .evdev_util import EvdevUtil
from .yaml_serializable import YamlSerializable

"""
VALID_BUTTONS are all of the possible buttons on a VEIKK device (afaik --
this may not be exhaustive, especially with newer VEIKK devices). Any
mappings outside of this list will be ignored.
"""
VALID_BUTTONS = [
    # keypad buttons
    ecodes.BTN_0, ecodes.BTN_1, ecodes.BTN_2, ecodes.BTN_3, ecodes.BTN_4,
    ecodes.BTN_5, ecodes.BTN_6, ecodes.BTN_7, ecodes.BTN_8, ecodes.BTN_9,
    ecodes.BTN_NORTH, ecodes.BTN_SOUTH, ecodes.BTN_WEST, ecodes.BTN_EAST,
    ecodes.BTN_TOOL_DOUBLETAP, ecodes.BTN_WHEEL,
    # stylus buttons
    ecodes.BTN_TOUCH, ecodes.BTN_STYLUS, ecodes.BTN_STYLUS2,
]
VALID_BUTTONS_SET = set(VALID_BUTTONS)


class VeikkConfig(YamlSerializable):
    """
    This serves as the model for the configuration of the veikkd daemon.

    TODO: validate buttons in map
    TODO: figure out how to model the pen configuration.
    """

    # reusable noop instance
    _noop = NoopCommand()

    def __init__(self,
                 btn_map: Dict[Union[str, KeyCode], Command] = None,
                 pen_transform: PenTransformCommand = None):
        if btn_map is None:
            btn_map = {}
        if pen_transform is None:
            pen_transform = PenTransformCommand()

        # if btn_map keys are strings, convert them to keycodes
        # wrap .keys() in list() because we modify the keys as we iterate
        for key in list(btn_map.keys()):
            if isinstance(key, str):
                btn_map[EvdevUtil.str_to_keycode(key)] = btn_map[key]
                del btn_map[key]

        self._btn_map = btn_map
        self._pen_transform = pen_transform
        super(VeikkConfig, self).__init__()

    def map_button(self, code: KeyCode, command: Command) -> None:
        """
        Assigns a command to a keycode
        :param code:
        :param command:
        """
        if code in VALID_BUTTONS_SET:
            self._btn_map[code] = command

    def unmap_button(self, code: KeyCode) -> None:
        """
        Unsets a mapping by mapping it to noop
        :param code:
        """
        self.map_button(code, self._noop)

    def execute_event(self,
                      event: InputEvent,
                      devices: Tuple[UInput, UInput]) -> None:
        """
        Execute an event if present
        :param event:
        :param devices:
        :return:
        """
        if event.type == ecodes.EV_ABS:
            self._pen_transform.execute(event, devices)
        elif event.type == ecodes.EV_KEY and event.code in self._btn_map:
            self._btn_map[event.code].execute(event, devices)

    def _to_yaml_dict(self) -> Dict:
        """
        Serialization. See YamlSerializable
        :return:
        """
        return {
            "btn_map": {
                EvdevUtil.keycode_to_str(keycode): command
                for keycode, command in self._btn_map.items()
            },
            "pen_transform": self._pen_transform
        }
