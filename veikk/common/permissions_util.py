import os
import pwd
from subprocess import Popen
from typing import Callable, Mapping, List


class PermissionsUtil:
    """
    Helper function run_as to run a program as another user (non-root).
    """

    @staticmethod
    def run_as(program: List[str], user: str, **kwargs):
        Popen(program,
              preexec_fn=PermissionsUtil._get_demote_fn(user),
              env=PermissionsUtil._get_env(user),
              **kwargs)

    @staticmethod
    def _get_env(user: str) -> Mapping[str, str]:
        """
        Merges some important variables of the environment of the other user
        into the current env.
        :param user:    user to copy the environment of
        :return:        modified env
        """
        pw_record = pwd.getpwnam(user)

        env = os.environ.copy()
        env['HOME'] = pw_record.pw_dir
        env['LOGNAME'] = pw_record.pw_name

        # default cwd to user home directory
        env['PWD'] = env['HOME']

        # default X parameters; run graphical applications on the main display
        env['DISPLAY'] = ':0'
        env['XAUTHORITY'] = env['HOME'] + '/.Xauthority'

        return env

    @staticmethod
    def _get_demote_fn(user: str) -> Callable[[], None]:
        """
        Returns a lambda that will be called before Popen is run that
        changes the current process's user and group ids.
        :param user:
        :return:
        """
        pw_record = pwd.getpwnam(user)

        def result():
            os.setgid(pw_record.pw_uid)
            os.setuid(pw_record.pw_gid)
        return result
