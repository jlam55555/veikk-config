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
                 button_map: Dict[Union[str, KeyCode], Command] = None,
                 pen_transform: PenTransformCommand = None):
        if button_map is None:
            button_map = {}
        if pen_transform is None:
            pen_transform = PenTransformCommand()

        # if btn_map keys are strings, convert them to keycodes
        # wrap .keys() in list() because we modify the keys as we iterate
        for key in list(button_map.keys()):
            if isinstance(key, str):
                button_map[EvdevUtil.str_to_keycode(key)] = button_map[key]
                del button_map[key]

        self._button_map = button_map
        self._pen_transform = pen_transform
        super(VeikkConfig, self).__init__()

    def _verify(self) -> None:
        """
        Verify that the configuration is valid. Checks all subcommands.
        """
        for btn, cmd in self._button_map.items():
            assert EvdevUtil.is_valid_keycode(btn)
            assert not isinstance(cmd, PenTransformCommand)
            cmd._verify()

        if self._pen_transform is not None:
            self._pen_transform._verify()

    def map_button(self, code: KeyCode, command: Command) -> None:
        """
        Assigns a command to a keycode
        :param code:
        :param command:
        """
        if code in VALID_BUTTONS_SET:
            self._button_map[code] = command

    def unmap_button(self, code: KeyCode) -> None:
        """
        Unsets a mapping by mapping it to noop
        :param code:
        """
        self.map_button(code, self._noop)

    def map_pen(self, command: PenTransformCommand) -> None:
        """
        Assigns a mapping for the pen.
        """
        self._pen_transform = command

    def get_button_command(self, code: Union[KeyCode, str]) -> Command:
        """
        Gets the command associated with a keycode
        :param code:
        :return:
        """
        if isinstance(code, str):
            code = EvdevUtil.str_to_keycode(code)

        return self._button_map[code]

    def get_pen_command(self) -> PenTransformCommand:
        """
        Returns the current pen transform
        :return:
        """
        return self._pen_transform

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
        elif event.type == ecodes.EV_KEY and event.code in self._button_map:
            self._button_map[event.code].execute(event, devices)

    def _to_yaml_dict(self) -> Dict:
        """
        Serialization. See YamlSerializable
        :return:
        """
        return {
            "button_map": {
                EvdevUtil.keycode_to_str(keycode): command
                for keycode, command in self._button_map.items()
            },
            "pen_transform": self._pen_transform
        }
