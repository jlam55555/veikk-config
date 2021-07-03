from typing import Dict, Tuple, List

import wx
from wx import MouseEvent
from functools import reduce


def get_monitors() -> List[wx.Rect]:
    """
    Gets the offsets and sizes (in pixels) of all the monitors as a list of
    tuples (x_offset, y_offset, width, height).
    """
    return [wx.Display(idx).GetGeometry()
            for idx in range(wx.Display.GetCount())]


def get_total_screen_rect() -> wx.Rect:
    """
    Returns the size of all the screens put together (the smallest rectangle
    containing the unions of all of the displays).
    """
    return reduce(lambda acc, screen: acc.Union(screen),
                  get_monitors(),
                  wx.Rect())


class SelectableFrame(wx.Frame):
    """
    Select an area of the screen. Overlays a semitransparent window onto the
    screen and draws a rectangle as you drag it. Works with multiple monitors.

    Source: https://stackoverflow.com/a/57348580
    """
    selection_start, selection_end = None, None

    def __init__(self, parent=None, id=wx.ID_ANY, title=''):
        sx, sy = wx.Display(0).GetGeometry().GetPosition().Get()

        frame_style = wx.NO_BORDER

        padding = 100
        frame_size = get_total_screen_rect().Inflate(padding).GetSize()
        frame_pos = (-sx-padding, -sy-padding)

        wx.Frame.__init__(self, parent, id, title,
                          size=frame_size, pos=frame_pos, style=frame_style)

        # mapping_rect will be the output of the selectable frame
        self.mapping_rect = None

        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.Show()
        self.SetTransparent(127)

    def on_mouse_move(self, event: MouseEvent):
        if event.Dragging() and event.LeftIsDown():
            self.selection_end = event.GetPosition()
            self.Refresh()

    def on_mouse_down(self, event: wx.MouseEvent):
        self.selection_start = event.GetPosition()

    def on_mouse_up(self, _: wx.MouseEvent):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.Destroy()

    def on_paint(self, _: wx.MouseEvent):
        if self.selection_start is None or self.selection_end is None:
            return

        self.mapping_rect = wx.Rect(self.selection_start, self.selection_end)

        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('red', 1))
        dc.SetBrush(wx.Brush('red', wx.BRUSHSTYLE_CROSSDIAG_HATCH))
        dc.DrawRectangle(self.mapping_rect)


class SelectableFrameApp(wx.App):
    """
    wxPython app to run the screen mapping selection GUI and return the
    selected rectangle and screen size.
    """

    def __init__(self):
        self.frame = None
        super(SelectableFrameApp, self).__init__()

    def OnInit(self):
        self.frame = SelectableFrame()
        return True

    def get_total_screen_rect(self) -> Tuple[int, int, int, int]:
        return get_total_screen_rect().GetSize().Get()

    def get_monitors(self) -> List[Tuple[int, int, int, int]]:
        return list(map(wx.Rect.Get, get_monitors()))

    def get_mapping_rect(self) -> Dict[str, Tuple]:
        """
        Runs the app and returns the mapped screen area.
        """
        self.MainLoop()
        return self.frame.mapping_rect.Get()
