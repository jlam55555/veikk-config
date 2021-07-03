from typing import Tuple, Dict
from evdev import UInput, ecodes, InputEvent

from .command import Command, CommandType
from ...common.transform_matrix_util import AffineTransform2D, \
    AffineTransform1D


class PenTransformCommand(Command):
    """
    Perform an affine transformation on the pen coordinates. Is handled
    separately from the other commands (which manage button actions).
    """

    def __init__(self,
                 coord_transform: AffineTransform2D = None,
                 pressure_transform: AffineTransform1D = None) -> None:
        if coord_transform is None:
            coord_transform = AffineTransform2D((1, 0, 0,
                                                 0, 1, 0,
                                                 0, 0, 1))
        if pressure_transform is None:
            pressure_transform = AffineTransform1D((1, 0,
                                                    0, 1))

        self._coords: Tuple[int, int] = (0, 0)
        self._coord_transform = coord_transform
        self._pressure_transform = pressure_transform
        super(PenTransformCommand, self).__init__(CommandType.PEN_TRANSFORM)

    def execute(self,
                event: InputEvent,
                devices: Tuple[UInput, UInput]) -> None:
        """
        Note: if either X or Y get updated, then the transformed X and Y will
        both get emitted. This may be a little inefficient, but it's necessary
        if there's any rotation. Plus, there will still be the same number of
        SYN events, so it probably won't affect performance much.
        :param event:
        :param devices:
        :return:
        """

        # pressure transform
        if event.code == ecodes.ABS_PRESSURE:
            value = int(self._pressure_transform.transform((event.value,))[0])
            devices[0].write(event.type, event.code, value)

        # screen mapping transform
        elif event.code == ecodes.ABS_X or event.code == ecodes.ABS_Y:
            if event.code == ecodes.ABS_X:
                self._coords = (event.value, self._coords[1])
            else:
                self._coords = (self._coords[0], event.value)
            value = self._coord_transform.transform(self._coords)
            devices[0].write(event.type, ecodes.ABS_X, int(value[0]))
            devices[0].write(event.type, ecodes.ABS_Y, int(value[1]))

        # maybe tilt support in the future?

    def _to_yaml_dict(self) -> Dict:
        return {
            'coord_transform': self._coord_transform,
            'pressure_transform': self._pressure_transform
        }
