import veikk.daemon

# TODO: remove; for testing -- a sample command map
# simple mapping for testing
from evdev import ecodes
from veikk.common.command.program_command import ProgramCommand
from veikk.common.command.keycombo_command import KeyComboCommand
from veikk.common.command.command import CommandTriggerMap, CommandTrigger, CommandMap
from veikk.common.command.pentransform_command import PenTransformCommand
pen_command = PenTransformCommand()
command_map: CommandMap = {
    ecodes.ABS_X: pen_command,
    ecodes.ABS_Y: pen_command,
    ecodes.ABS_PRESSURE: pen_command,
    ecodes.BTN_TOUCH: KeyComboCommand([ecodes.BTN_TOUCH]),
    ecodes.BTN_STYLUS: KeyComboCommand([ecodes.BTN_STYLUS]),
    ecodes.BTN_STYLUS2: KeyComboCommand([ecodes.BTN_STYLUS2]),
    ecodes.BTN_0: ProgramCommand(['echo', 'Hello, world!', ';', 'read'], True),
    ecodes.BTN_1: ProgramCommand(['htop'], True, start_new_session=True),
    ecodes.BTN_2: KeyComboCommand([ecodes.KEY_LEFTCTRL,
                                   ecodes.KEY_RIGHTSHIFT,
                                   ecodes.KEY_E]),
    ecodes.BTN_3: ProgramCommand(['krita'], run_as_user='jon'),
    ecodes.BTN_4: ProgramCommand([
        'xvkbd', '-no-jump-pointer', '-text', 'Hello, world'],
        trigger_type_map=CommandTriggerMap(CommandTrigger.KEYUP)),

    # have to manually specify a user for this to work.
    ecodes.BTN_5: ProgramCommand(['google-chrome'], run_as_user='jon'),

    ecodes.BTN_6: KeyComboCommand([ecodes.KEY_VOLUMEUP]),
    ecodes.BTN_7: KeyComboCommand([ecodes.BTN_LEFT]),

    ecodes.BTN_WEST: KeyComboCommand([ecodes.KEY_LEFTBRACE]),
    ecodes.BTN_EAST: KeyComboCommand([ecodes.KEY_RIGHTBRACE]),
    ecodes.BTN_NORTH: KeyComboCommand([ecodes.KEY_EQUAL]),
    ecodes.BTN_SOUTH: KeyComboCommand([ecodes.KEY_MINUS]),
    ecodes.BTN_TOOL_DOUBLETAP: KeyComboCommand([ecodes.KEY_LEFTCTRL,
                                                ecodes.KEY_0])
}

if __name__ == '__main__':
    veikk.daemon.main(default_command_map=command_map)
