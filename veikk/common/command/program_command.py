from subprocess import Popen
from typing import List
from evdev import InputEvent, ecodes

from .command import Command, CommandType, CommandTriggerMap, CommandTrigger
from ..permissions_util import PermissionsUtil


class ProgramCommand(Command):
    """
    Map a button or gesture to execute a regular Linux command.
    """

    def __init__(self,
                 program: List[str],
                 run_in_terminal: bool = False,
                 run_as_user: str = None,
                 trigger_type_map: CommandTriggerMap
                 = CommandTriggerMap(CommandTrigger.KEYDOWN),
                 **popen_options):

        if run_in_terminal:
            program = ['xterm', '-e', ' '.join(program)]

        self._user = run_as_user
        self._program = program
        self._trigger_type_map = trigger_type_map
        self._popen_options = popen_options

        super(ProgramCommand, self).__init__(CommandType.PROGRAM)

    def execute(self, event: InputEvent, _):
        """
        Execute program command. We use the event to see if it is one of the
        trigger types. For terminal commands, use xterm as the shell because
        there are too many options for launching other shells and xterm
        is standard.
        :param event:   original event
        :param _:       uinput devices -- unused
        :return:
        """
        if event.type == ecodes.EV_SYN or \
                not self._trigger_type_map[event.value]:
            return

        if self._user is not None:
            PermissionsUtil.run_as(self._program, self._user,
                                   **self._popen_options)
        else:
            Popen(self._program, **self._popen_options)
