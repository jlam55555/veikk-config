import subprocess
from argparse import Namespace
from os import environ

from evdev import ecodes
from pydbus import SystemBus

from veikk.cli.coordinate_mapping._screen_area_getter import _ScreenAreaGetter
from veikk.cli.coordinate_mapping.xlib_screen_area_getter import XlibScreenAreaGetter
from veikk.common.command.pentransform_command import PenTransformCommand
from veikk.common.constants import VEIKK_DBUS_OBJECT, VEIKK_DBUS_INTERFACE
from veikk.common.transform_matrix_util import Orientation, TransformMatrixUtil
from veikk.common.veikk_config import VeikkConfig
from veikk.common.veikk_daemon_dbus import VeikkDaemonDbus
from ..common.command.command import KeyCode, Command
from ..common.command.keycombo_command import KeyComboCommand
from ..common.command.program_command import ProgramCommand
from ..common.evdev_util import EvdevUtil
from ..common import constants


class CommandHandlers:
    """
    Handle commands emitted from running the
    """

    def __init__(self):
        self._dbus_object: VeikkDaemonDbus \
            = SystemBus().get(VEIKK_DBUS_OBJECT, VEIKK_DBUS_INTERFACE)

    @staticmethod
    def _format_config(input_str: str) -> str:
        """
        Formats YAML text differently so that it is easily identifiable.
        :param input_str:   string to format
        :return             formatted string.
        """
        return f'\n##### begin YAML\n\n{input_str}\n##### end YAML\n'

    @staticmethod
    def edit_config(_) -> None:
        """
        Edit configuration file. Try to use default editor, if set
        in the EDITOR environment variable.

        TODO: the sudo promotion in _run_as_root() doesn't work well to
            preserve environment variables, so this may not end up using
            the user's $EDITOR envvar

        :param _:
        """
        if environ.get('EDITOR') is not None:
            subprocess.run([environ.get('EDITOR'),
                            constants.VEIKK_CONFIG_LOCATION])
        else:
            # use nano as a default editor, will probably exist
            subprocess.run(['xterm', '-e', '/usr/bin/nano',
                            constants.VEIKK_CONFIG_LOCATION])

    def get_config(self, args: Namespace) -> None:
        """
        Get the current configuration.
        :param args:
        """
        config_yaml = self._dbus_object.GetCurrentConfig(0)
        config = VeikkConfig.load_yaml(config_yaml)

        sp = args.subparser
        if sp == 'button' or sp == 'b':
            print(f'Current button mapping for {args.keycode}:')
            print(self._format_config(
                config.get_button_command(args.keycode).dump_yaml()))
        elif sp == 'pen' or sp == 'p':
            print('Current pen transform:')
            print(self._format_config(config.get_pen_command().dump_yaml()))
        else:
            print('Current configuration:')
            print(self._format_config(config_yaml))

    def set_button_config(self, args: Namespace) -> None:
        """
        Sets a button configuration.

        # TODO: input defaults
        :param args:
        """
        keycode: KeyCode = ecodes.ecodes[input('Enter keycode to map: ')]

        map_type = ''
        while map_type not in ['p', 'k']:
            map_type = input('Map to [p]rogram or [k]ey combination? ')

        # program
        if map_type == 'p':
            shell_cmd = input('Input shell command to execute: ')
            run_as_user = input('Enter user to run command as: ')
            run_in_terminal = input('Run in terminal? [f] ') \
                                  .lower() in ['t', 'true']
            command = ProgramCommand(shell_cmd=shell_cmd,
                                     run_in_terminal=run_in_terminal,
                                     run_as_user=run_as_user)

        # keyboard combination
        else:
            keycodes_str = \
                input('Enter mapped keycodes as a comma-separated list: ')
            keycodes = \
                list(map(lambda keycode_str: ecodes.ecodes[keycode_str],
                         keycodes_str.upper().replace(' ', '').split(',')))
            command = KeyComboCommand(keycodes=keycodes)

        # update daemon
        assert isinstance(command, Command)
        self._dbus_object.MapButton(0, keycode, command.dump_yaml())

    def set_pen_config(self, args: Namespace) -> None:
        """
        Sets the pen configuration.

        # TODO: input defaults
        :param args:
        """
        if args.visual:
            try:
                from veikk.cli.coordinate_mapping.wx_screen_area_getter \
                    import WxScreenAreaGetter
            except ImportError:
                print('You must install wxPython to use the visual pen'
                      ' mapping tool.')
                return
            screen_area_getter = WxScreenAreaGetter()
        else:
            screen_area_getter = XlibScreenAreaGetter()

        assert isinstance(screen_area_getter, _ScreenAreaGetter)

        # print total monitor info
        total_screen_rect = screen_area_getter.get_total_screen_rect()
        print(f'Total screen area: {total_screen_rect[0]}x'
              f'{total_screen_rect[1]}px')

        # print monitor info, if more than one monitor
        monitor_rects = screen_area_getter.get_monitors()
        if len(monitor_rects) > 1:
            print('  Monitors info:')
            for i, monitor_rect in enumerate(monitor_rects):
                print(f'    Monitor {i + 1}:\n'
                      f'      Offset x: {monitor_rect[0]}px\n'
                      f'      Offset y: {monitor_rect[1]}px\n'
                      f'      Width:    {monitor_rect[2]}px\n'
                      f'      Height:   {monitor_rect[3]}px')

        # get mapping orientation
        orientation = ''
        while orientation not in Orientation.__members__:
            orientation = input('Orientation [NORMAL]: ')
        orientation = Orientation[orientation]

        # get mapping rectangle and print information
        mapped_rect = screen_area_getter.get_mapping_rect()

        # convert to transformation matrix and print
        transform_matrix = TransformMatrixUtil.get_rotation_scale_offset_matrix(
            orientation, total_screen_rect[0], total_screen_rect[1],
            mapped_rect[0], mapped_rect[1], mapped_rect[2], mapped_rect[3]
        )
        print(f'Generated transform matrix: {transform_matrix.get_matrix()}')

        # TODO: pressure mapping

        # set the mapping
        transform_command = PenTransformCommand(transform_matrix)
        self._dbus_object.MapPen(0, transform_command.dump_yaml())

    def apply_config(self, _) -> None:
        """
        Apply the settings in the conf file to the daemon.
        """
        self._dbus_object.LoadConfigFromFile(0, '')

    def save_config(self, _) -> None:
        """
        Save the settings from the daemon to the conf file
        """
        self._dbus_object.SaveConfigToFile(0, '')

    @staticmethod
    def show_devices(_) -> None:
        """
        List all connected VEIKK devices. Each device created by the driver
        will end in the word "Bundled". (Additional evdev devices created by
        the mapping daemon will end in "Pen" or "Keyboard".)
        """
        veikk_devices = ['- ' + device.name[:-7]
                         for device in EvdevUtil.get_initial_devices()
                         if device.name.endswith('Bundled')]
        if len(veikk_devices) > 0:
            print('Current VEIKK devices:\n' + '\n'.join(veikk_devices))
        else:
            print('No connected VEIKK devices found.')

    @staticmethod
    def show_version(_) -> None:
        """
        Show veikk-config version number.
        """
        print(constants.VEIKK_CONFIG_VERSION)
