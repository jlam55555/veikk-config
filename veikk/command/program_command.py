import subprocess
from typing import List
from evdev import InputEvent

from veikk.command.command import Command, CommandType


class ProgramCommand(Command):
    def __init__(self, program: List[str], run_in_terminal: bool = True):
        self._program = program
        self._run_in_terminal = run_in_terminal
        super(ProgramCommand, self).__init__(CommandType.KEYCOMBO)

    def execute(self, event: InputEvent):
        if self._run_in_terminal:
            subprocess.call(['xterm', '-e', ' '.join(self._program)])
        else:
            subprocess.call(self._program)
