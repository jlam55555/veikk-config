from typing import Tuple, Dict
from evdev import UInput, ecodes, InputEvent

from .command import Command, CommandType

# TODO: turn these into classes; may need utility functions to generate these
#   from more human-friendly forms, and need to make them implement
#   YamlSerializable as well, which is easier with a class
AffineTransform2D = Tuple[float, float, float,
                          float, float, float,
                          float, float, float]
AffineTransform1D = Tuple[float, float]


class PenTransformCommand(Command):
    """
    Perform an affine transformation on the pen coordinates. Is handled
    separately from the other commands (which manage button actions).
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

    def _to_yaml_dict(self) -> Dict:
        return {
            'coord_transform': self._coord_transform,
            'pressure_transform': self._pressure_transform
        }
