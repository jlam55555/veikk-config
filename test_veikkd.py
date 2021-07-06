import veikk.daemon

# TODO: remove; for testing -- a sample command map
# simple mapping for testing
from evdev import ecodes

from veikk.common.command.pentransform_command import PenTransformCommand, AffineTransform2D
from veikk.common.command.program_command import ProgramCommand
from veikk.common.command.keycombo_command import KeyComboCommand
from veikk.common.command.command import CommandTriggerMap, CommandTrigger
from veikk.common.veikk_config import VeikkConfig

config = VeikkConfig({
    ecodes.BTN_TOUCH: KeyComboCommand([ecodes.BTN_TOUCH]),
    ecodes.BTN_STYLUS: KeyComboCommand([ecodes.BTN_STYLUS]),
    ecodes.BTN_STYLUS2: KeyComboCommand([ecodes.BTN_STYLUS2]),
    ecodes.BTN_0: ProgramCommand('echo "Hello, world!"; read', True),
    ecodes.BTN_1: ProgramCommand('htop', True,
                                 popen_options={'start_new_session': True}),
    ecodes.BTN_2: KeyComboCommand([ecodes.KEY_LEFTCTRL,
                                   ecodes.KEY_RIGHTSHIFT,
                                   ecodes.KEY_E]),
    ecodes.BTN_3: ProgramCommand('krita', run_as_user='jon'),
    ecodes.BTN_4: ProgramCommand('xvkbd -no-jump-pointer -text "Hello, world"',
        triggers_on=CommandTriggerMap(CommandTrigger.KEYUP)),

    # have to manually specify a user for this to work.
    ecodes.BTN_5: ProgramCommand('google-chrome', run_as_user='jon'),

    ecodes.BTN_6: KeyComboCommand([ecodes.KEY_VOLUMEUP]),
    ecodes.BTN_7: KeyComboCommand([ecodes.BTN_LEFT]),

    ecodes.BTN_WEST: KeyComboCommand([ecodes.KEY_LEFTBRACE]),
    ecodes.BTN_EAST: KeyComboCommand([ecodes.KEY_RIGHTBRACE]),
    ecodes.BTN_NORTH: KeyComboCommand([ecodes.KEY_EQUAL]),
    ecodes.BTN_SOUTH: KeyComboCommand([ecodes.KEY_MINUS]),
    ecodes.BTN_TOOL_DOUBLETAP: KeyComboCommand([ecodes.KEY_LEFTCTRL,
                                                ecodes.KEY_0])
}, PenTransformCommand(AffineTransform2D((0.0, 0.1564453125, 0.78125, -0.3014521782674011, 0.0, 0.9323985978968453, 0.0, 0.0, 1.0))))

a = config.dump_yaml()
b = VeikkConfig.load_yaml(a)
c = b.dump_yaml()

print(a, b, c)
print(a == c)

if __name__ == '__main__':
    veikk.daemon.main(default_config=config)
