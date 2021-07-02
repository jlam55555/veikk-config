import wx
from wx import MouseEvent

selectionOffset, selectionSize = '', ''


class SelectableFrame(wx.Frame):
    """
    Select an area of the screen. Overlays a semitransparent window onto the
    screen and draws a rectangle as you drag it.

    TODO: does this work with multiple monitors?

    Source: https://stackoverflow.com/a/57348580
    """
    c1, c2 = None, None

    def __init__(self, parent=None, id=wx.ID_ANY, title=''):
        wx.Frame.__init__(self, parent, id, title, size=wx.DisplaySize(),
                          style=~wx.SYSTEM_MENU)

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
        print(selectionOffset, selectionSize)

    def OnPaint(self, event):
        global selectionOffset, selectionSize
        if self.c1 is None or self.c2 is None:
            return

        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('red', 1))
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0), wx.TRANSPARENT))

        dc.DrawRectangle(self.c1.x, self.c1.y,
                         self.c2.x - self.c1.x, self.c2.y - self.c1.y)
        selectionOffset = f'{self.c1.x}x{self.c1.y}'
        selectionSize = f'{self.c2.x - self.c1.x}x{self.c2.y - self.c1.y}'

    def PrintPosition(self, pos):
        return f'{pos.x}x{pos.y}'


class MyApp(wx.App):

    def OnInit(self):
        frame = SelectableFrame()
        return True
