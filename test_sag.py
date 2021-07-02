# testing the screen area grabber
# will remove this script as soon as I find out whether
# it works with multiple monitors

from veikk.cli.coordinate_mapping.screen_area_grabber import MyApp, \
    selectionSize, selectionOffset

app = MyApp(redirect=False)
app.MainLoop()
print(f'offset: {selectionOffset}, size: {selectionSize}')
