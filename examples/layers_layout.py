import pyglet
from vui import RootLayout, HStackLayout, VStackLayout, View, LayersLayout

from colors import *

window = pyglet.window.Window(resizable=True)
ui = RootLayout(
    window,
    LayersLayout(
        View(background_color=BLACK),
        HStackLayout(
            VStackLayout(View(min_height=100, flex_height=False),
                        View(background_color=RED),
                        min_width=200,
                        flex_width=False),
            VStackLayout(
                View(background_color=TEAL),
                View(),
            ))))

pyglet.app.run()