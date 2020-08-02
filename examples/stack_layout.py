import pyglet
from pygui import RootLayout, HStackLayout, VStackLayout, View

window = pyglet.window.Window(resizable=True)
ui = RootLayout(
    window,
    HStackLayout(
        VStackLayout(View(background_color=(0, 0x33, 0),
                          min_height=100,
                          flex_height=False),
                     View(background_color=(0x4c, 0x8c, 0x4a)),
                     min_width=200,
                     flex_width=False),
        VStackLayout(
            View(background_color=(0x7f, 0, 0)),
            View(background_color=(0xf0, 55, 45)),
        )))

pyglet.app.run()