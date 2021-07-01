from typing import Tuple, Dict
from evdev import UInput, ecodes, InputEvent
from yaml import Node, Dumper, Loader

from .command import Command, CommandType
from ..yaml_serializable import YamlSerializable


class AffineTransformationMatrix(YamlSerializable):
    """
    Representation of an affine transformation matrix (in row-major order).

    This allows for a linear coordinate transformation along with a possible
    offset. For an affine transformation in N-dimensional space, the
    transformation matrix is (N+1)x(N+1), and the input vector gets augmented
    with a 1 in the last coordinate.

    It will be assumed that the transform matrix is valid, but checks can be
    put in _verify_tuple(). Additionally, the transform() method may assume
    that the transformation matrix is in the standard form for simplicity
    (e.g., ignoring the last row of the matrix entirely -- these are not
    needed in an affine transformation).

    This matches the behavior when using the `xinput` tool and setting the
    `Coordinate Transformation Matrix` property on a pointer device -- setting
    the coordinate transform here or there are functionally equivalent, but
    the CLI helps you generate the transform matrix.

    https://wiki.ubuntu.com/X/InputCoordinateTransformation
    https://en.wikipedia.org/wiki/Transformation_matrix#Affine_transformations
    """

    def __init__(self, matrix: Tuple):
        self._matrix = tuple(map(float, matrix))
        self._verify_tuple()
        super(AffineTransformationMatrix, self).__init__()

    def _verify_tuple(self): ...

    def transform(self, vec: Tuple) -> Tuple: ...

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

    def transform(self, vec: Tuple[float, float]) -> Tuple[float, float]:
        m11, m12, m13, m21, m22, m23, _, _, _ = self._matrix
        v1, v2 = vec
        return m11 * v1 + m12 * v2 + m13 * 65536,\
            m21 * v1 + m22 * v2 + m23 * 65536


class AffineTransform1D(AffineTransformationMatrix):
    def _verify_tuple(self) -> bool:
        """
        TODO: more advanced check
        :return:
        """
        return len(self._matrix) == 4

    def transform(self, vec: Tuple[float]) -> Tuple[float]:
        return self._matrix[0] * vec[0] + self._matrix[1],


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
