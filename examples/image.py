import os
import pyglet
from vui import RootLayout, Image

import colors

path = os.path.join(os.path.dirname(__file__), 'grid.png')
window = pyglet.window.Window(resizable=True)
ui = RootLayout(
    window,
    Image(path, alloc_background_color=colors.TEAL))

pyglet.app.run()