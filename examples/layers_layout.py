import pyglet
from vui import RootLayout, HStackLayout, VStackLayout, View, LayersLayout

import colors

window = pyglet.window.Window(resizable=True)
ui = RootLayout(
    window,
    LayersLayout(
        View(background_color=colors.BLACK),
        HStackLayout(
            VStackLayout(View(min_height=100, flex_height=False),
                         View(background_color=colors.RED),
                         min_width=200,
                         flex_width=False),
            VStackLayout(
                View(background_color=colors.TEAL),
                View(),
            ))))

pyglet.app.run()