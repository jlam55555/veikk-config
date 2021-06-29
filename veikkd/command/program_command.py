import os
import pwd
from subprocess import Popen
from typing import List, Mapping, Callable
from evdev import InputEvent, ecodes

from veikkd.command.command \
    import Command, CommandType, CommandTriggerMap, CommandTrigger


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

        if self._user is not None:
            self._env = self._get_env()
            self._demote_fn = self._get_demote_fn()

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
            Popen(self._program,
                  preexec_fn=self._demote_fn,
                  env=self._env,
                  **self._popen_options)
        else:
            Popen(self._program, **self._popen_options)

    def _get_env(self) -> Mapping[str, str]:
        pw_record = pwd.getpwnam(self._user)

        env = os.environ.copy()
        env['HOME'] = pw_record.pw_dir
        env['LOGNAME'] = pw_record.pw_name

        # default cwd to user home directory
        env['PWD'] = env['HOME']

        # default X parameters; run graphical applications on the main display
        env['DISPLAY'] = ':0'
        env['XAUTHORITY'] = env['HOME'] + '/.Xauthority'

        return env

    def _get_demote_fn(self) -> Callable[[], None]:
        pw_record = pwd.getpwnam(self._user)

        def result():
            os.setgid(pw_record.pw_uid)
            os.setuid(pw_record.pw_gid)
        return result
