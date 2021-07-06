from subprocess import Popen
from typing import List, Dict, Mapping, Union
from evdev import InputEvent, ecodes

from .command import Command, CommandType, CommandTriggerMap, CommandTrigger
from ..permissions_util import PermissionsUtil


class ProgramCommand(Command):
    """
    Map a button or gesture to execute a regular Linux command.
    """

    def __init__(self,
                 shell_cmd: str,
                 run_in_terminal: bool = False,
                 run_as_user: str = None,
                 triggers_on: Union[List[str], CommandTriggerMap]
                 = CommandTriggerMap(CommandTrigger.KEYDOWN),
                 popen_options: Mapping = None):

        self._original_shell_cmd = shell_cmd

        if run_in_terminal:
            shell_cmd = f'xterm -e {repr(shell_cmd)}'
        if popen_options is None:
            popen_options = {}
        if run_as_user is None:
            run_as_user = 'root'
        if isinstance(triggers_on, list):
            triggers_on = CommandTriggerMap(*triggers_on)

        self._run_in_terminal = run_in_terminal
        self._user = run_as_user
        self._shell_cmd = shell_cmd
        self._triggers_on = triggers_on
        self._popen_options = popen_options

        super(ProgramCommand, self).__init__(CommandType.PROGRAM)

    def _verify(self) -> None:
        """
        Perform any necessary checks.

        TODO: what checks should be made?
        """
        pass

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
                not self._triggers_on[event.value]:
            return

        if self._user is not None:
            PermissionsUtil.run_as(self._shell_cmd, self._user,
                                   shell=True,
                                   **self._popen_options)
        else:
            Popen(self._shell_cmd, shell=True, **self._popen_options)

    def _to_yaml_dict(self) -> Dict:
        """
        For serialization
        :return:
        """
        return {
            'shell_cmd': self._original_shell_cmd,
            'run_in_terminal': self._run_in_terminal,
            'run_as_user': self._user,
            'triggers_on': self._triggers_on.to_list(),
            'popen_options': self._popen_options
        }
