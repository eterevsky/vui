import pyglet
from vui import RootLayout, HStackLayout, VStackLayout, View

from colors import *

window = pyglet.window.Window(resizable=True)
ui = RootLayout(
    window,
    HStackLayout(
        VStackLayout(View(background_color=BLACK,
                          min_height=100,
                          flex_height=False),
                     View(background_color=RED),
                     min_width=200,
                     flex_width=False),
        VStackLayout(
            View(background_color=TEAL),
            View(background_color=SAND),
        )))

pyglet.app.run()