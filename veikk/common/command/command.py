from abc import ABCMeta
from enum import Enum
from typing import Tuple, List, Union
from evdev import InputEvent, UInput
from yaml import Dumper, Node, Loader

from veikk.common.yaml_serializable import YamlSerializable

KeyCode = int


class CommandType(Enum):
    NOOP = 0
    KEY_COMBO = 1
    PROGRAM = 2
    PEN_TRANSFORM = 3


class CommandTrigger(Enum):
    """
    When to trigger a command for a keyboard event. Used in ProgramCommand.
    Order is important -- these correspond to the event.value when a button
    is released, pressed, and held, respectively.
    """
    KEYUP = 0
    KEYDOWN = 1
    KEYPRESS = 2


class CommandTriggerMap:
    """
    Used to indicate which trigger type(s) trigger an action.
    Used in ProgramCommand.

    Sample usage: trigger on both keyup and keydown

        from daemon.command.command import CommandTrigger as trigger
        ProgramTrigger(..., CommandTriggerMap(trigger.KEYDOWN, trigger.KEYUP))
    """

    def __init__(self, *trigger_map: Union[str, CommandTrigger]):
        self._trigger_map = (CommandTrigger.KEYUP in trigger_map
                             or CommandTrigger.KEYUP.name in trigger_map,
                             CommandTrigger.KEYDOWN in trigger_map
                             or CommandTrigger.KEYDOWN.name in trigger_map,
                             CommandTrigger.KEYPRESS in trigger_map
                             or CommandTrigger.KEYPRESS.name in trigger_map)
        super(CommandTriggerMap, self).__init__()

    def __getitem__(self, item):
        return self._trigger_map[item]

    def to_list(self) -> List[str]:
        """
        Converts self to a simple serializable list of strings.
        :return:
        """
        return [CommandTrigger(trigger_type).name
                for trigger_type, is_trigger in enumerate(self._trigger_map)
                if is_trigger]


class Command(YamlSerializable):
    """
    Some action/callback/handler for an input event from the driver. E.g.,
    button press, gesture, or pen mappings. Button and pen mappings are handled
    separately.
    """

    def __init__(self, command_type: CommandType):
        self._type = command_type
        super(Command, self).__init__()

    def execute(self,
                event: InputEvent,
                devices: Tuple[UInput, UInput]) -> None:
        """
        Dispatch command when the associated event is emitted from the driver.
        :param event:       the original event from the driver
        :param devices:     the pen and keyboard virtual devices to dispatch
                            events to
        """
        raise NotImplementedError()
