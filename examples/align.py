"""Demonstration of different alignments.

The program draws a resizable window with two rows. First is a HStackLayout
of elements with `flex_width=False` and second with `flex_width=True`. Each cell
contains a `View` with different values of `halign` and `valign`. The area
allocated for the view by the layout is shown in teal, and the active area of
the view is shown in red.
"""

import pyglet
from vui import (RootLayout, HStackLayout, VStackLayout, View, LayersLayout,
                 HAlign, VAlign, Spacer, View)

from colors import RED, BLACK, TEAL

vstack = VStackLayout(background_color=BLACK)

for flex_width in (False, True):
    hstack = HStackLayout(background_color=TEAL)
    for halign in (HAlign.LEFT, HAlign.CENTER, HAlign.FILL):
        for valign in (VAlign.TOP, VAlign.CENTER, VAlign.FILL):
            if hstack.children:
                hstack.add_child(
                    Spacer(min_width=10,
                           flex_width=False,
                           background_color=BLACK))
            hstack.add_child(
                View(min_width=80,
                        min_height=80,
                        flex_width=flex_width,
                        halign=halign,
                        valign=valign,
                        background_color=RED))

    if vstack.children:
        vstack.add_child(Spacer(min_height=10, flex_height=False))
    vstack.add_child(hstack)

window = pyglet.window.Window(width=1000, resizable=True)
ui = RootLayout(window, vstack)

pyglet.app.run()