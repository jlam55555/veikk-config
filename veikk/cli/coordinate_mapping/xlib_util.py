from Xlib import X, display
from Xlib.ext import randr


# TODO: cite this

# display = display.Display(':0')
#
# print(display.screen_count())
#
# root = display.screen().root
# print(root.get_geometry().width)
# print(root.get_geometry().height)

# d = display.Display()
# s = d.screen()
# window = s.root.create_window(0, 0, 1, 1, 1, s.root_depth)
#
# res = randr.get_screen_resources(window)
# for mode in res.modes:
#     w, h = mode.width, mode.height
#     print(f'width: {w}, height: {h}')

def find_mode(id, modes):
    for mode in modes:
        if id == mode.id:
            return f'{mode.width}x{mode.height}'


def get_display_info():
    d = display.Display(':0')
    screen_count = d.screen_count()
    default_screen = d.get_default_screen()
    result = []
    screen = 0
    info = d.screen(screen)
    window = info.root

    res = randr.get_screen_resources(window)
    for output in res.outputs:
        params = d.xrandr_get_output_info(output, res.config_timestamp)
        if not params.crtc:
            continue
        crtc = d.xrandr_get_crtc_info(params.crtc, res.config_timestamp)
        modes = set()
        for mode in params.modes:
            modes.add(find_mode(mode, res.modes))
        result.append({
            'name': params.name,
            'resolution': f'{crtc.width}x{crtc.height}',
            'available_resolutions': list(modes)
        })

    return result

