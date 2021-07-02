from enum import Enum

from veikk.common.command.pentransform_command import AffineTransform2D


class Orientation(Enum):
    NORMAL = 0,
    CCW_90 = 1,
    FLIPPED = 2
    CW_90 = 3


class TransformMatrixUtil:
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
