from subprocess import Popen
from typing import List
from evdev import InputEvent, ecodes

from veikk.command.command \
    import Command, CommandType, CommandTriggerMap, CommandTrigger


class ProgramCommand(Command):
    """
    Map a button or gesture to execute a regular Linux command.
    """

    def __init__(self,
                 program: List[str],
                 run_in_terminal: bool = False,
                 trigger_type_map: CommandTriggerMap
                 = CommandTriggerMap(CommandTrigger.KEYDOWN),
                 **popen_options):
        if run_in_terminal:
            program = ['xterm', '-e', ' '.join(program)]

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
        :param _:       uinput device -- unused
        :return:
        """
        if event.type == ecodes.EV_SYN or \
                not self._trigger_type_map[event.value]:
            return

        Popen(self._program, **self._popen_options)
