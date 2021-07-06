from typing import Tuple, List
from functools import reduce

import wx
from wx import MouseEvent

from veikk.cli.coordinate_mapping._screen_area_getter import _ScreenAreaGetter


def _get_monitors() -> List[wx.Rect]:
    """
    Gets the offsets and sizes (in pixels) of all the monitors as a list of
    tuples (x_offset, y_offset, width, height).
    """
    return [wx.Display(idx).GetGeometry()
            for idx in range(wx.Display.GetCount())]


def _get_total_screen_rect() -> wx.Rect:
    """
    Returns the size of all the screens put together (the smallest rectangle
    containing the unions of all of the displays).
    """
    return reduce(lambda acc, screen: acc.Union(screen),
                  _get_monitors(),
                  wx.Rect())


class _SelectableFrame(wx.Frame):
    """
    Select an area of the screen. Overlays a semitransparent window onto the
    screen and draws a rectangle as you drag it. Works with multiple monitors.

    PascalCased functions to match wxPython convention.

    Based on: https://stackoverflow.com/a/57348580
    """
    selection_start, selection_end = None, None

    def __init__(self, parent=None, id=wx.ID_ANY, title=''):
        sx, sy = wx.Display(0).GetGeometry().GetPosition().Get()

        frame_style = wx.NO_BORDER

        padding = 100
        frame_size = _get_total_screen_rect().Inflate(padding).GetSize()
        frame_pos = (-sx-padding, -sy-padding)

        wx.Frame.__init__(self, parent, id, title,
                          size=frame_size, pos=frame_pos, style=frame_style)

        # mapping_rect will be the output of the selectable frame
        self.mapping_rect = None

        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.Show()
        self.SetTransparent(127)

    def OnMouseMove(self, event: MouseEvent):
        if event.Dragging() and event.LeftIsDown():
            self.selection_end = event.GetPosition()
            self.Refresh()

    def OnMouseDown(self, event: wx.MouseEvent):
        self.selection_start = event.GetPosition()

    def OnMouseUp(self, _: wx.MouseEvent):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.Destroy()

    def OnPaint(self, _: wx.MouseEvent):
        if self.selection_start is None or self.selection_end is None:
            return

        self.mapping_rect = wx.Rect(self.selection_start, self.selection_end)

        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('red', 1))
        dc.SetBrush(wx.Brush('red', wx.BRUSHSTYLE_CROSSDIAG_HATCH))
        dc.DrawRectangle(self.mapping_rect)


class _SelectableFrameApp(wx.App):
    """
    wxPython app to run the screen mapping selection GUI and return the
    selected rectangle and screen size.
    """
    def __init__(self):
        self.frame = None
        super(_SelectableFrameApp, self).__init__()

    def OnInit(self):
        self.frame = _SelectableFrame()
        return True


class WxScreenAreaGetter(_ScreenAreaGetter):

    def __init__(self):
        self._app = _SelectableFrameApp()

    def get_total_screen_rect(self) -> Tuple[int, int, int, int]:
        return _get_total_screen_rect().GetSize().Get()

    def get_monitors(self) -> List[Tuple[int, int, int, int]]:
        return list(map(wx.Rect.Get, _get_monitors()))

    def get_mapping_rect(self) -> Tuple[int, int, int, int]:
        """
        Runs the app and returns the mapped screen area.
        """
        self._app.MainLoop()
        return self._app.frame.mapping_rect.Get()
