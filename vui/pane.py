import pyglet.shapes  # type: ignore
from typing import Optional, Tuple, Union

from . import event
from .observable import Attribute, MaybeObservable, Observable, make_observable

# Type used for specifying a rectangular area as (x0, y0, x1, y1) where (x0, y0)
# is the bottom left corner and (x1, y1) is top right.
Coords = Tuple[float, float, float, float]


class Pane(event.EventDispatcher):
    """An area in a window owned by a view.

    The pane consists of two nested rectangles. The inner rectangle is defined
    by `coords` and represents the area handled by the view. Mouse events for
    this area are handled by the pane and the view attached to it is expected
    to render its contents within this rectangle.

    The outer rectangle is defined by `alloc_coords` and consists of the area
    in the parent pane that was allocated for a given view. It may exactly match
    the dimensions of the outer rectangle, or it might be smaller in which case
    it is up to the view to determine its exact location based on the
    *alignment* of the view.

    Both `coords` and `alloc_coords` have the form (x0, y0, x1, y1) where
    (x0, y0) is the bottom left and (x1, y1) is the top right corner.

    Observable attributes:
        alloc_coords: the area allocated to the pane. Usually set by the parent
            layout and observed by the attached view.
        coords: the "active" area of the pane. Mouse events are tracked within
            this area, and the attached view is expected to be rendered in it.
            Initially initialized with the same coordinates as `alloc_coords`,
            updated by the attached view based on its dimensions, flex_*,
            horizontal and vertical alignment and alloc_coords.
        background_color: background color represented by a tuple R, G, B of
            integers in the range 0 <= X < 256. Will fill the active area of the
            pane.
        mouse_pos: position of the mouse cursor when mouse is over the active
            area of the pane, None otherwise.
    """
    alloc_coords: Attribute[Coords] = Attribute('alloc_coords_')
    coords: Attribute[Coords] = Attribute('coords_')
    alloc_background_color: Attribute[Tuple[int, int, int]] = Attribute(
        'alloc_background_color_')
    background_color: Attribute[Tuple[int, int,
                                      int]] = Attribute('background_color_')
    mouse_pos: Attribute[Optional[Tuple[float,
                                        float]]] = Attribute('mouse_pos_')

    def __init__(self,
                 x0: float,
                 y0: float,
                 x1: float,
                 y1: float,
                 background_color: MaybeObservable[Tuple[int, int,
                                                           int]] = None,
                 alloc_background_color: MaybeObservable[Tuple[int, int,
                                                           int]] = None):
        self.alloc_coords_: Observable[Coords] = Observable((x0, y0, x1, y1))
        self.coords_: Observable[Coords] = Observable((x0, y0, x1, y1))
        self.coords_.observe(self._prepare_background_draw)
        self.mouse_pos_: Observable[Optional[Tuple[float,
                                                   float]]] = Observable(None)

        self.alloc_background_color_: Observable[Optional[Tuple[
            int, int, int]]] = make_observable(alloc_background_color)
        self.background_color_: Observable[Optional[Tuple[
            int, int, int]]] = make_observable(background_color)
        self.alloc_background_color_.observe(self._prepare_background_draw)
        self.background_color_.observe(self._prepare_background_draw)
        self._prepare_background_draw()

    def __str__(self):
        x0, y0, x1, y1 = self.coords
        ax0, ay0, ax1, ay1 = self.alloc_coords
        return 'Pane({}, {}, {}, {} | {}, {}, {}, {})'.format(
            ax0, ay0, ax1, ay1, x0, y0, x1, y1)

    def remove_observer(self, observer):
        self.alloc_coords_.remove_observer(observer)
        self.coords_.remove_observer(observer)
        self.mouse_pos_.remove_observer(observer)
        self.background_color_.remove_observer(observer)

    @property
    def width(self):
        return self.coords[2] - self.coords[0]

    @property
    def height(self):
        return self.coords[3] - self.coords[1]

    def _prepare_background_draw(self, *args):
        if self.background_color is not None:
            x0, y0, x1, y1 = self.coords
            self._background_shape = pyglet.shapes.Rectangle(
                x=x0,
                y=y0,
                width=(x1 - x0),
                height=(y1 - y0),
                color=self.background_color)
        else:
            self._background_shape = None

        if self.alloc_background_color is not None:
            x0, y0, x1, y1 = self.alloc_coords
            self._alloc_background_shape = pyglet.shapes.Rectangle(
                x=x0,
                y=y0,
                width=(x1 - x0),
                height=(y1 - y0),
                color=self.alloc_background_color)
        else:
            self._alloc_background_shape = None

    def _draw_background(self):
        if self._alloc_background_shape is not None:
            self._alloc_background_shape.draw()
        if self._background_shape is not None:
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

    def swap_alloc_background(self, alloc_background_color_):
        """Replace background_color with a new external observable."""
        self.alloc_background_color_.remove_observer(self)
        self.alloc_background_color_ = alloc_background_color_
        self._prepare_background_draw()


Pane.register_event_type('on_draw')
Pane.register_event_type('on_mouse_drag')
Pane.register_event_type('on_mouse_press')
Pane.register_event_type('on_mouse_release')
Pane.register_event_type('on_mouse_scroll')


class DummyPane(Pane):
    def __init__(self):
        super().__init__(0, 0, 0, 0)

    def __str__(self):
        return 'DummyPane'

    def on_draw(self):
        pass

    def contains(self, x, y):
        return False


DUMMY_PANE = DummyPane()
