"""
This file serves as a fallback in case wxpython is not installed.
"""
from typing import Tuple, List
from Xlib.display import Display

from veikk.cli.coordinate_mapping._screen_area_getter import _ScreenAreaGetter


class XlibScreenAreaGetter(_ScreenAreaGetter):

    @classmethod
    def get_monitors(cls) -> List[Tuple[int, int, int, int]]:
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

    @classmethod
    def get_total_screen_rect(cls) -> Tuple[int, int]:
        display = Display()
        screen = display.screen()
        return screen['width_in_pixels'], screen['height_in_pixels']

    @classmethod
    def get_mapping_rect(cls) -> Tuple[int, int, int, int]:
        """
        Prompt for screen area mapping

        TODO: specify value defaults
        :return:    mapped screen rect
        """
        print('Enter desired screen mapping:')
        offset_x = int(input('  Offset x: '))
        offset_y = int(input('  Offset y: '))
        width = int(input('  Width: '))
        height = int(input('  Height: '))

        return offset_x, offset_y, width, height
