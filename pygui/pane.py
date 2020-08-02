import pyglet.shapes  # type: ignore
from typing import Optional, Tuple, Union

from . import event
from .observable import Attribute, Observable, make_observable


class Pane(event.EventDispatcher):
    """A rectangular area in a window.

    This class dispatches mouse events related to the controlled area and draws
    its background.

    The class has 3 observable attributes:

    coords: a tuple the coordinates of bottom left and top right corners, can
      be set by the external code (usually a Layout class)
    background_color: background color represented by a tuple R, G, B of
      integers in the range 0 <= X < 256.
    mouse_pos: position of the mouse cursor when mouse is over the pane, None
      otherwise

    """

    coords: Attribute[Tuple[float, float, float, float]] = Attribute('coords_')
    background_color: Attribute[Tuple[int, int,
                                      int]] = Attribute('background_color_')
    mouse_pos: Attribute[Optional[Tuple[float,
                                        float]]] = Attribute('mouse_pos_')

    def __init__(self, x0: float, y0: float, x1: float, y1: float,
                 background: Union[Observable, Tuple[int, int, int]] = None):
        self.coords_: Observable[Tuple[float, float, float, float]] = Observable(
            (x0, y0, x1, y1))
        self.coords_.observe(self._on_coords_change)
        self.mouse_pos_: Observable[Optional[Tuple[float,
                                                   float]]] = Observable(None)

        self.background_color_: Observable[Optional[Tuple[
            int, int, int]]] = make_observable(background)
        self.background_color_.observe(self._prepare_background_draw)
        self._prepare_background_draw()

    def __str__(self):
        x0, y0, x1, y1 = self.coords
        return 'Pane({}, {}, {}, {})'.format(x0, y0, x1, y1)

    def remove_observer(self, observer):
        self.coords_.remove_observer(observer)
        self.mouse_pos_.remove_observer(observer)
        self.background_color_.remove_observer(observer)

    @property
    def width(self):
        return self.coords[2] - self.coords[0]

    @property
    def height(self):
        return self.coords[3] - self.coords[1]

    def _on_coords_change(self, coords):
        self._prepare_background_draw()

    def _prepare_background_draw(self, *args):
        if self.background_color is None:
            self._background_shape = None
            return
        x0, y0, x1, y1 = self.coords
        self._background_shape = pyglet.shapes.Rectangle(
            x=x0, y=y0, width=(x1 - x0), height=(y1 - y0),
            color=self.background_color)

    def _draw_background(self):
        if self._background_shape is None:
            return
        self._background_shape.draw()

    @event.priority(1)
    def on_draw(self):
        self._draw_background()

    def contains(self, x, y):
        x0, y0, x1, y1 = self.coords
        return x0 <= x < x1 and y0 <= y < y1

    def swap_background(self, background_color_):
        """Replace background_color with a new external observable."""
        self.background_color_.remove_observer(self)
        self.background_color_ = background_color_
        self._prepare_background_draw()


Pane.register_event_type('on_draw')
Pane.register_event_type('on_mouse_drag')
Pane.register_event_type('on_mouse_press')
Pane.register_event_type('on_mouse_release')
Pane.register_event_type('on_mouse_scroll')

DUMMY_PANE = Pane(0, 0, 0, 0, Observable(None))
