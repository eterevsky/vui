# vui
vui is a cross-platform GUI framwork, built on top of Pyglet. It is currently
in early stage of development. The aim is to build a simple pythonic API that
could be used to build UI apps and games.

The framework is built around the hierarchy of UI elements represented by
classes inheriting from `View`. A view class can be attached to a (single)
`Pane` object. `Pane` is a simple class representing a rectangular area
in the window. This class also plays the role of host for mouse events.

Some of the views can contain other views. Such views are called "layouts".
A layout class is a `View` that contains the logic of subdiving its pane into
panes for its children.

Various UI classes are glued together with `Observable` values and attributes.
Functions and methods can be registed as listeners to an observable value. These
listeners are called whenever the value is changed. Most attributes of UI values
are observable, including pane dimentions, mouse position and so on.

In addition to `Observable` vui makes use of `events` module forked from Pyglet
events. As a rule, whenever an event can be thought about as changes of some
value, it should be represented as `Observable`. But some events like `on_draw`
don't fit this model and are represented as events.
