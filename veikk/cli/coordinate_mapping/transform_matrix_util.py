from enum import Enum
from typing import Tuple

from yaml import Dumper, Node, Loader

from ...common.constants import VEIKK_MAPPED_DIM
from ...common.yaml_serializable import YamlSerializable


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

    def __getitem__(self, item: Tuple) -> float: ...

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
        return m11 * v1 + m12 * v2 + m13 * VEIKK_MAPPED_DIM,\
            m21 * v1 + m22 * v2 + m23 * VEIKK_MAPPED_DIM

    def __getitem__(self, item: Tuple[int, int]) -> float:
        """
        Simple numpy-style tuple indexing. Coordinates are (y, x) order.
        :param item:
        :return:
        """
        y, x = item
        return self._matrix[3*y + x]


class AffineTransform1D(AffineTransformationMatrix):
    def _verify_tuple(self) -> bool:
        """
        TODO: more advanced check
        :return:
        """
        return len(self._matrix) == 4

    def transform(self, vec: Tuple[float]) -> Tuple[float]:
        return self._matrix[0] * vec[0] + self._matrix[1],


class Orientation(Enum):
    NORMAL = 0,
    CCW_90 = 1,
    FLIPPED = 2
    CW_90 = 3


class TransformMatrixUtil:
    """
    Static methods to calculate the coordinate transform matrix from a set
    of more interpretable values:

    - rotation (quantized to 90deg)
    - mapped screen rectangle
    - total screen size (all monitors)

    The output mapping rectangle should do exactly as what X does with the
    "Coordinate Transform Matrix" property.
    """

    _rotations = {
        Orientation.NORMAL: (1, 0, 0, 0, 1, 0, 0, 0, 1),
        Orientation.CCW_90: (0, 1, 0, -1, 0, 1, 0, 0, 1),
        Orientation.FLIPPED: (-1, 0, 1, 0, -1, 1, 0, 0, 1),
        Orientation.CW_90: (0, -1, 1, 1, 0, 0, 0, 0, 1),
    }

    @staticmethod
    def matrix3_multiply(m: AffineTransform2D,
                         n: AffineTransform2D) -> AffineTransform2D:
        """
        All this mess just to avoid having an extra library to install (i.e.,
        numpy). We only use this to generate the transform matrix (this does
        not get used during mapping), so it's okay if it's slow.

        Builds in row-major order, since that is what AffineTransform2D uses.
        :param m:   matrix 1
        :param n:   matrix 2
        :return:    matrix product mn
        """
        result = [0] * 9
        for i in range(9):
            x, y = i % 3, i // 3
            for j in range(3):
                result[i] += m[y, j] * n[j, x]
        return AffineTransform2D(tuple(result))

    @classmethod
    def get_rotation_scale_offset_matrix(cls,
                                         orientation: Orientation,
                                         screen_width: int,
                                         screen_height: int,
                                         offset_x: int,
                                         offset_y: int,
                                         width_x: int,
                                         width_y: int) -> AffineTransform2D:
        return cls.matrix3_multiply(
            cls.get_scale_offset_matrix(screen_width, screen_height,
                                        offset_x, offset_y,
                                        width_x, width_y),
            cls.get_rotation_matrix(orientation)
        )

    @classmethod
    def get_rotation_matrix(cls, orientation: Orientation) -> AffineTransform2D:
        return AffineTransform2D(cls._rotations[orientation])

    @staticmethod
    def get_scale_offset_matrix(screen_width: int,
                                screen_height: int,
                                offset_x: int,
                                offset_y: int,
                                width_x: int,
                                width_y: int) -> AffineTransform2D:
        offset_x_norm, offset_y_norm = offset_x / screen_width, \
                                       offset_y / screen_height
        scale_x, scale_y = width_x / screen_width, \
                           width_y / screen_height
        return AffineTransform2D((scale_x, 0, offset_x_norm,
                                  0, scale_y, offset_y_norm,
                                  0, 0, 1))
