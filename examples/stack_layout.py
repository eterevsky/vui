import pyglet
from vui import RootLayout, HStackLayout, VStackLayout, View

import colors

window = pyglet.window.Window(resizable=True)
ui = RootLayout(
    window,
    HStackLayout(
        VStackLayout(View(background_color=colors.BLACK,
                          min_height=100,
                          flex_height=False),
                     View(background_color=colors.RED),
                     min_width=200,
                     flex_width=False),
        VStackLayout(
            View(background_color=colors.TEAL),
            View(background_color=colors.SAND),
        )))

pyglet.app.run()