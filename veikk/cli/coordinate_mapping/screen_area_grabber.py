import wx
from wx import MouseEvent
from functools import reduce


def get_total_screen_rect() -> wx.Rect:
    """
    Returns the size of all the screens put together.
    """
    return reduce(lambda acc, next: acc.Union(next),
                  [wx.Display(id).GetGeometry() for id in range(wx.Display.GetCount())],
                  wx.Rect())


class SelectableFrame(wx.Frame):
    """
    Select an area of the screen. Overlays a semitransparent window onto the
    screen and draws a rectangle as you drag it.

    TODO: does this work with multiple monitors?

    Source: https://stackoverflow.com/a/57348580
    """
    c1, c2 = None, None

    def __init__(self, parent=None, id=wx.ID_ANY, title=''):
        sx, sy = wx.Display(0).GetGeometry().GetPosition().Get()

        frame_style = wx.NO_BORDER

        padding = 100
        wx.Frame.__init__(self, parent, id, title, size=get_total_screen_rect().Inflate(padding).GetSize(),
                          pos=(-sx-padding, -sy-padding), style=frame_style)

        # mapping_rect will be the output of the selectable frame
        self.mapping_rect = None

        self.menubar = wx.MenuBar(wx.MB_DOCKABLE)
        self.filem = wx.Menu()
        self.filem.Append(wx.ID_EXIT, '&Transparency')
        self.menubar.Append(self.filem, '&File')
        # self.SetMenuBar(self.menubar)

        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MENU, self.OnTrans)

        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.Show()
        self.transp = False
        self.OnTrans()

    def OnTrans(self):
        self.SetTransparent(255 if self.transp else 127)
        self.transp = not self.transp

    def OnMouseMove(self, event: MouseEvent):
        if event.Dragging() and event.LeftIsDown():
            self.c2 = event.GetPosition()
            self.Refresh()

    def OnMouseDown(self, event):
        self.c1 = event.GetPosition()

    def OnMouseUp(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.Destroy()

    def OnPaint(self, event):
        global selectionOffset, selectionSize
        if self.c1 is None or self.c2 is None:
            return

        self.mapping_rect = wx.Rect(self.c1, self.c2)

        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('red', 1))
        dc.SetBrush(wx.Brush('red', wx.BRUSHSTYLE_CROSSDIAG_HATCH))
        dc.DrawRectangle(self.mapping_rect)                         

    def PrintPosition(self, pos):
        return f'{pos.x}x{pos.y}'


class MyApp(wx.App):

    def OnInit(self):
        self.frame = SelectableFrame()
        return True


def get_mapping_parameters():
    a = MyApp()
    a.MainLoop()

    return {
        'screen_size': get_total_screen_rect().GetSize().Get(),
        'mapping_rect': a.frame.mapping_rect.Get()
    }
