from typing import Tuple, Dict, Union, List
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
                 coord_transform: Union[List[float], AffineTransform2D] = None,
                 pressure_transform: Union[List[float], AffineTransform1D]
                 = None) -> None:
        if coord_transform is None:
            coord_transform = AffineTransform2D((1, 0, 0,
                                                 0, 1, 0,
                                                 0, 0, 1))
        elif isinstance(coord_transform, list):
            coord_transform = AffineTransform2D(tuple(coord_transform))

        if pressure_transform is None:
            pressure_transform = AffineTransform1D((1, 0,
                                                    0, 1))
        elif isinstance(pressure_transform, list):
            pressure_transform = AffineTransform1D(tuple(pressure_transform))

        self._coords: Tuple[int, int] = (0, 0)
        self._coord_transform = coord_transform
        self._pressure_transform = pressure_transform
        super(PenTransformCommand, self).__init__(CommandType.PEN_TRANSFORM)

    def _verify(self) -> None:
        """
        Perform any necessary checks.

        TODO: what checks should be performed?
        """
        pass

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

        # TODO: maybe support tilt support in the future? will probably either
        #   be a passthrough or a linear transform like the pressure transform

    def _to_yaml_dict(self) -> Dict:
        return {
            'coord_transform': list(self._coord_transform.get_matrix()),
            'pressure_transform': list(self._pressure_transform.get_matrix())
        }
