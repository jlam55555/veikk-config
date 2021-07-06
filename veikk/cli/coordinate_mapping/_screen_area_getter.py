from abc import ABC
from typing import List, Tuple


class _ScreenAreaGetter(ABC):
    """
    Gets information about the monitors and the total screen rectangle.
    """

    def get_monitors(self) -> List[Tuple[int, int, int, int]]:
        """
        Gets the offsets and sizes (in pixels) of all the monitors as a list of
        tuples.
        :return     list of tuples (x_offset, y_offset, width, height) for each
                    monitor
        """
        raise NotImplementedError()

    def get_total_screen_rect(self) -> Tuple[int, int]:
        """
        Returns the size of all the screens put together (the smallest rectangle
        containing the unions of all of the displays).
        :return:    (screen_width, screen_height)
        """
        raise NotImplementedError()

    def get_mapping_rect(self) -> Tuple[int, int, int, int]:
        """
        Gets the mapped screen rectangle.
        :return:    (x_offset, y_offset, width, height) of the selected
                    screen mapped area
        """
        raise NotImplementedError()
