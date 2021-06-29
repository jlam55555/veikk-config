from typing import Tuple
from evdev import UInput, ecodes, InputEvent

from veikkd.command.command import Command, CommandType

AffineTransform2D = Tuple[float, float, float,
                          float, float, float,
                          float, float, float]
AffineTransform1D = Tuple[float, float]


class PenTransformCommand(Command):
    """
    Perform an affine transformation on the pen coordinates.
    """

    def __init__(self,
                 coord_transform: AffineTransform2D = None,
                 pressure_transform: AffineTransform1D = None) -> None:
        if coord_transform is None:
            coord_transform = (1, 0, 0,
                               0, 1, 0,
                               0, 0, 1)
        if pressure_transform is None:
            pressure_transform = (1, 0)

        self._prev_coords: Tuple[int, int] = (0, 0)
        self._coord_transform = coord_transform
        self._pressure_transform = pressure_transform
        super(PenTransformCommand, self).__init__(CommandType.PEN_TRANSFORM)

    def execute(self,
                event: InputEvent,
                devices: Tuple[UInput, UInput]) -> None:
        if event.code == ecodes.ABS_PRESSURE:
            devices[0].write(event.type, event.code, event.value)
        elif event.code == ecodes.ABS_X or event.code == ecodes.ABS_Y:
            devices[0].write_event(event)

        # maybe tilt support in the future?
