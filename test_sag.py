# testing the screen area grabber
# will remove this script as soon as I find out whether
# it works with multiple monitors

from veikk.cli.coordinate_mapping.screen_area_grabber import get_mapping_parameters
from veikk.cli.coordinate_mapping.transform_matrix_util import TransformMatrixUtil, Orientation

screen_map_parms = get_mapping_parameters()

screen_width, screen_height = screen_map_parms['screen_size']
offset_x, offset_y, width_x, width_y = screen_map_parms['mapping_rect']

orientation = Orientation.CCW_90

print(screen_map_parms)
print(TransformMatrixUtil.get_rotation_scale_offset_matrix(orientation, screen_width, screen_height, offset_x, offset_y, width_x, width_y)._matrix)
