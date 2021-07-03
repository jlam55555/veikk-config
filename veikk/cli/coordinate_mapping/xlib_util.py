"""
This file serves as a fallback in case wxpython is not installed.
"""

from typing import Tuple, List

from Xlib.display import Display


def get_monitors() -> List[Tuple[int, int, int, int]]:
    """
    Gets the offsets and sizes (in pixels) of all the monitors as a list of
    tuples (x_offset, y_offset, width, height).
    """
    display = Display()
    root = display.screen().root
    resources = root.xrandr_get_screen_resources()._data
    config_timestamp = resources['config_timestamp']

    outputs_data = []
    for output in resources['outputs']:
        crtc = display\
            .xrandr_get_output_info(output, config_timestamp)._data['crtc']
        if crtc == 0:
            continue

        monitor_info = display\
            .xrandr_get_crtc_info(crtc, config_timestamp)._data
        outputs_data.append((monitor_info['x'], monitor_info['y'],
                             monitor_info['width'], monitor_info['height']))
    return outputs_data


def get_total_screen_rect() -> Tuple[int, int]:
    """
    Returns the size of all the screens put together (the smallest rectangle
    containing the unions of all of the displays).
    """
    display = Display()
    screen = display.screen()
    return screen['width_in_pixels'], screen['height_in_pixels']
