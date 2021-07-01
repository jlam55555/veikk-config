from typing import Tuple, Dict
from evdev import UInput, ecodes, InputEvent
from yaml import Node, Dumper, Loader

from .command import Command, CommandType
from ..yaml_serializable import YamlSerializable


class AffineTransformationMatrix(YamlSerializable):

    def __init__(self, matrix: Tuple):
        self._matrix = tuple(map(float, matrix))
        self._verify_tuple()
        super(AffineTransformationMatrix, self).__init__()

    def _verify_tuple(self): ...

    @classmethod
    def to_yaml(cls,
                dumper: Dumper,
                data: 'AffineTransformationMatrix') -> Node:
        """
        Overwrite with simpler constructor
        :param dumper:
        :param data:
        :return:
        """
        return dumper.represent_sequence(f'!{cls.__name__}',
                                         data._matrix)

    @classmethod
    def from_yaml(cls,
                  loader: Loader,
                  node: Node) -> 'YamlSerializable':
        return cls(loader.construct_sequence(node))


class AffineTransform2D(AffineTransformationMatrix):
    def _verify_tuple(self) -> bool:
        """
        TODO: more advanced check
        :return:
        """
        return len(self._matrix) == 9


class AffineTransform1D(AffineTransformationMatrix):
    def _verify_tuple(self) -> bool:
        """
        TODO: more advanced check
        :return:
        """
        return len(self._matrix) == 4


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
