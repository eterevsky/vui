import os
import pyglet
import pyglet.image
from vui import RootLayout, HStackLayout, VStackLayout, View, Image, VAlign, HAlign

import colors

path = os.path.join(os.path.dirname(__file__), 'grid.png')
data = pyglet.image.load(path)
window = pyglet.window.Window(resizable=True)
ui = RootLayout(
    window,
    HStackLayout(
        VStackLayout(Image(data, alloc_background_color=colors.TEAL),
                     Image(data, alloc_background_color=colors.SAND)),
        VStackLayout(
            Image(data, alloc_background_color=colors.RED),
            Image(data,
                  halign=HAlign.FILL,
                  valign=VAlign.FILL,
                  alloc_background_color=colors.PURPLE))))

print(ui)
pyglet.app.run()