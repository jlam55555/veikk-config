from enum import Enum
from evdev import InputEvent, UInput

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


class CommandTriggerMap(tuple):
    """
    Used to indicate which trigger type(s) trigger an action.
    Used in ProgramCommand.

    Sample usage: trigger on both keyup and keydown

        from veikk.command.command import CommandTrigger as trigger
        ProgramTrigger(..., CommandTriggerMap(trigger.KEYDOWN, trigger.KEYUP))
    """
    def __new__(cls, *trigger_types: CommandTrigger):
        return tuple.__new__(CommandTriggerMap,
                             (CommandTrigger.KEYUP in trigger_types,
                              CommandTrigger.KEYDOWN in trigger_types,
                              CommandTrigger.KEYPRESS in trigger_types))


class Command:
    """
    Some action/callback/handler for an input event from the driver. E.g.,
    button press, gesture, or pen remappings.
    """

    def __init__(self, command_type: CommandType):
        self._type = command_type

    def execute(self, event: InputEvent, device: UInput) -> None:
        """
        Dispatch command when the associated event is emitted from the driver.
        :param event:       the original event from the driver
        :param device:      the virtual device to emit events on
        """
        ...
