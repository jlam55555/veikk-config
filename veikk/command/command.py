from enum import Enum

from evdev import InputEvent


class CommandType(Enum):
    KEYCOMBO = 0
    METHOD = 1


class Command:
    """
    An action spawned by a button press or gesture. Can be either a key
    combination or a command.
    """

    def __init__(self, command_type: CommandType):
        self._type = command_type

    def execute(self, event: InputEvent) -> None:
        """
        Dispatch command when the associated event is emitted from the driver.
        :param event:   the original event from the driver
        """
        ...
