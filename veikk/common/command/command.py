from enum import Enum
from typing import Tuple
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


class CommandTriggerMap(tuple, YamlSerializable):
    """
    Used to indicate which trigger type(s) trigger an action.
    Used in ProgramCommand.

    Sample usage: trigger on both keyup and keydown

        from daemon.command.command import CommandTrigger as trigger
        ProgramTrigger(..., CommandTriggerMap(trigger.KEYDOWN, trigger.KEYUP))
    """
    def __new__(cls, *trigger_types: CommandTrigger):
        return tuple.__new__(CommandTriggerMap,
                             (CommandTrigger.KEYUP in trigger_types,
                              CommandTrigger.KEYDOWN in trigger_types,
                              CommandTrigger.KEYPRESS in trigger_types))
    
    def __init__(self, *trigger_types: CommandTrigger):
        super(CommandTriggerMap, self).__init__()

    def _yaml_representer(self,
                          dumper: Dumper,
                          data: 'YamlSerializable') -> Node:
        """
        Serialize in the same form as the constructor.
        :param dumper:
        :param data:
        :return:
        """
        return dumper.represent_sequence(f'!{self.__class__.__name__}',
                                         [trigger_type.name
                                          for trigger_type in CommandTrigger
                                          if self[trigger_type.value]])

    def _yaml_constructor(self,
                          loader: Loader,
                          node: Node) -> 'YamlSerializable':
        """
        Deserialize with varargs constructor, not kwargs
        :param loader:
        :param node:
        :return:
        """
        return self.__class__.__new__(*loader.construct_sequence(node))


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
        ...
