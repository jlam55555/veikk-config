# testing the screen area grabber
# will remove this script as soon as I find out whether
# it works with multiple monitors
from veikk.cli.coordinate_mapping.xlib_screen_area_getter import get_total_screen_rect, get_monitors
from veikk.cli.coordinate_mapping.wx_screen_area_getter import SelectableFrameApp
from veikk.common.transform_matrix_util import TransformMatrixUtil, Orientation

print(get_total_screen_rect(), get_monitors())

sfa = SelectableFrameApp()
print(sfa.get_total_screen_rect(), sfa.get_monitors())

screen_width, screen_height = get_total_screen_rect()
offset_x, offset_y, width_x, width_y = mapping_rect = sfa.get_mapping_rect()

orientation = Orientation.CCW_90

print(mapping_rect)
print(TransformMatrixUtil.get_rotation_scale_offset_matrix(orientation, screen_width, screen_height, offset_x, offset_y, width_x, width_y)._matrix)
