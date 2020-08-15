"""Layout objects: views that contain other views.

Layout objects manage one or more child panes and views attached to them. They
propagate events and observables to child panes. All of layout classes except
for `RootLayout` themselves inherit are View objects. They are attached to a
`Pane`, which they subdivide into child panes.

A layout object a) manages the child pane dimensions, and b) propagates
events and observables from the parent pane to appropriate child panes.
In general, a layout object observes values on its own pane, and on child
views, and sets values on child panes. For instance: a child View may change its
`min_width` attribute, its parent layout will observe it and might change the
`width` attribute of the Pane to which this view is attached.

Provided layout objects:

* `RootLayout` — does not inherit from `View`. Adapts a `pyglet.window.Window`
  object to be used for the views hierarchy.
* `HStachLayout`, `VStackLayout` — divide their panes into columns/rows based on
  `derived_width` and `flex_width` / `derived_height` and `flex_height`
  attributes of the child views.
* `LayersLayout` — each child pane occupies the whole parent pane. The child
  `View`'s are drawn one after another. Events are propagated started at the
  top pane.
* (planned) `FloatingLayout` — one View draws the background for the whole
  parent pane and a number of panes floating on top at arbitrary coordinates.
"""

import enum
import pyglet  # type: ignore
from typing import List, Optional, Tuple, Union

from .event import EVENT_HANDLED, EVENT_UNHANDLED
from .observable import Attribute, Observable
from .pane import Pane
from .view import View


class RootLayout(object):
    """The root of the views hierarchy, wrapping a Pyglet window.

    This class creates a `Pane` covering the whole Pyglet window, converts
    Pyglet events into Pane events and observables.
    """
    def __init__(self, window: pyglet.window.Window, child: View = None):
        self.dragging_: Observable[bool] = Observable(False)
        self.child_pane = Pane(0, 0, window.width, window.height)
        self._child = child
        if child is not None:
            child.attach(self.child_pane)
        window.push_handlers(self)

    def __str__(self):
        content = ''
        if self.child is not None:
            content = '\n'
            for line in str(self.child).split('\n'):
                content += '  ' + line + '\n'

        return 'RootLayout({})'.format(content)

    @property
    def child(self) -> Optional[View]:
        return self._child

    @child.setter
    def child(self, value: View):
        if self._child is not None:
            self._child.detach()
        self._child = value
        self._child.attach(self.child_pane)

    def on_draw(self):
        self.child_pane.dispatch_event('on_draw')

    def on_mouse_enter(self, x, y):
        self.child_pane.mouse_pos = (x, y)

    def on_mouse_leave(self, x, y):
        self.child_pane.mouse_pos = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.child_pane.mouse_pos = (x, y)
        self.child_pane.dispatch_event('on_mouse_drag', x, y, dx, dy, buttons,
                                       modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.child_pane.mouse_pos = (x, y)

    def on_mouse_press(self, *args):
        self.child_pane.dispatch_event('on_mouse_press', *args)

    def on_mouse_release(self, *args):
        self.child_pane.dispatch_event('on_mouse_release', *args)

    def on_mouse_scroll(self, *args):
        self.child_pane.dispatch_event('on_mouse_scroll', *args)

    def on_resize(self, width, height):
        self.child_pane.alloc_coords = (0, 0, width, height)


class Orientation(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class StackLayout(View):
    """Common base class for HStackLayout and VStackLayout.

    Splits the pane into rows or columns. The sizes of the panes depend on
    `derived_width`/`derived_height` and `flex_width`/`flex_height` attributes
    of the child views. For children with `flex_* = False` the layout tries
    to make the panes with the width/height exactly equal to `derived_*` (except
    for the cases when the pane would overflow the parent pane). The extra space
    left after accounting for `derived_*` for all children is distributed
    equally between children with `flex_*` = True.
    """
    def __init__(self,
                 orientation: Orientation,
                 *children: View,
                 flex_width=True,
                 flex_height=True,
                 **kwargs):
        super().__init__(flex_width=flex_width,
                         flex_height=flex_height,
                         **kwargs)

        self.orientation = orientation
        self._mouseover_pane: Optional[Pane] = None
        self._dragging_pane = None
        self._dragging_button = 0

        self.children: List[View] = list(children)
        for child in children:
            child.derived_width_.observe(self._update_content_width)
            child.derived_height_.observe(self._update_content_height)

        self.content_width = self._calc_content_width()
        self.content_height = self._calc_content_height()

    def __str__(self):
        content = ''
        for child in self.children:
            for line in str(child).split('\n'):
                content += '\n  ' + line
            content += ','
        content += '\n'

        return '{}[{}]({})'.format(self.__class__.__name__, self.pane, content)

    def attach(self, pane: Pane):
        super().attach(pane)
        pane.coords_.observe(self._update)
        pane.mouse_pos_.observe(self._observe_mouse_pos)

        # Currently we first attach all the child views to empty panes,
        # and then resize them. This is not optimal, since a lot of code will be
        # executed twice. But this is conceptually simpler, so we'll do it for
        # v0. Will probably optimize later.

        x0, y0, x1, y1 = pane.coords
        if self.orientation == Orientation.HORIZONTAL:
            y0 = y1
        else:
            x1 = x0
        for child in self.children:
            child_pane = Pane(x0, y0, x1, y1)
            child.attach(child_pane)
        self._update()

    def detach(self):
        for child in self.children:
            child.detach()
        super().detach()

    def _find_child_pane(self, x, y) -> Optional[Pane]:
        """Returns the child contining (x, y) or None."""
        if (self._mouseover_pane is not None
                and self._mouseover_pane.contains(x, y)):
            return self._mouseover_pane
        for child in self.children:
            child_pane = child.pane
            assert child_pane is not None
            if child_pane.contains(x, y):
                return child_pane
        return None

    def on_draw(self):
        for child in self.children:
            child.pane.dispatch_event('on_draw')

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self._dragging_pane is None:
            self._dragging_button = buttons
            self._dragging_pane = self._find_child_pane(x, y)

        if self._dragging_pane:
            self._dragging_pane.dispatch_event('on_mouse_drag', x, y, dx, dy,
                                               buttons, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        pane = self._find_child_pane(x, y)
        if pane:
            return pane.dispatch_event('on_mouse_press', x, y, button,
                                       modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if button & self._dragging_button:
            self._dragging_pane = None
            self._dragging_button = 0
        pane = self._find_child_pane(x, y)
        if pane:
            return pane.dispatch_event('on_mouse_release', x, y, button,
                                       modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pane = self._find_child_pane(x, y)
        if pane:
            return pane.dispatch_event('on_mouse_scroll', x, y, scroll_x,
                                       scroll_y)

    def _observe_mouse_pos(self, pos: Optional[Tuple[float, float]]):
        if pos is None:
            if self._mouseover_pane is not None:
                self._mouseover_pane.mouse_pos = None
            return
        x, y = pos
        if self._mouseover_pane is not None:
            if self._mouseover_pane.contains(x, y):
                self._mouseover_pane.mouse_pos = pos
                return
            self._mouseover_pane.mouse_pos = None
        self._mouseover_pane = self._find_child_pane(x, y)
        if self._mouseover_pane is not None:
            self._mouseover_pane.mouse_pos = pos

    def _update_content_width(self, *args):
        self.content_width = self._calc_content_width()
        self._update()

    def _update_content_height(self, *args):
        self.content_height = self._calc_content_height()
        self._update()

    def _calc_content_width(self):
        raise NotImplementedError('Should be overridden')

    def _calc_content_height(self):
        raise NotImplementedError('Should be overridden')

    def _update(self, *args):
        raise NotImplementedError('Should be overridden')


class HStackLayout(StackLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(Orientation.HORIZONTAL, *args, **kwargs)

    def _calc_content_width(self):
        return sum(c.derived_width for c in self.children)

    def _calc_content_height(self):
        return max(c.derived_height for c in self.children)

    def _update(self, *args):
        x0, y0, x1, y1 = self.pane.coords
        width = x1 - x0

        count_flex = sum(child.flex_width for child in self.children
                         if not child.hidden)
        extra = (width - self.derived_width) / max(count_flex, 1)

        x = x0
        for child in self.children:
            if child.hidden:
                continue
            if extra <= 0 or not child.flex_width:
                next_x = min(x + child.derived_width, x1)
            else:
                next_x = x + child.derived_width + extra
            child.pane.alloc_coords = (x, y0, next_x, y1)
            x = next_x


class VStackLayout(StackLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(Orientation.VERTICAL, *args, **kwargs)

    def _calc_content_width(self):
        return max(c.derived_width for c in self.children)

    def _calc_content_height(self):
        return sum(c.derived_height for c in self.children)

    def _update(self, *args):
        x0, y0, x1, y1 = self.pane.coords
        height = y1 - y0

        count_flex = sum(child.flex_height for child in self.children
                         if not child.hidden)
        extra = (height - self.derived_height) / max(count_flex, 1)

        y = y1
        for child in self.children:
            if child.hidden:
                continue
            if extra <= 0 or not child.flex_height:
                next_y = max(y - child.derived_height, y0)
            else:
                next_y = y - child.derived_height - extra
            child.pane.alloc_coords = (x0, next_y, x1, y)
            y = next_y


class LayersLayout(View):
    def __init__(self, *children, **kwargs):
        super().__init__(**kwargs)
        self.children = children
        for child in children:
            child.derived_width_.observe(self._update_content_width)
            child.derived_height_.observe(self._update_content_height)

        self._update_content_width()
        self._update_content_height()

    def __str__(self):
        content = ''
        for child in self.children:
            for line in str(child).split('\n'):
                content += '\n  ' + line
            content += ','
        content += '\n'

        return '{}[{}]({})'.format(self.__class__.__name__, self.pane, content)

    def attach(self, pane: Pane):
        super().attach(pane)
        pane.coords_.observe(self._update_coords)
        pane.mouse_pos_.observe(self._observe_mouse_pos)

        x0, y0, x1, y1 = pane.coords
        for child in self.children:
            child_pane = Pane(x0, y0, x1, y1)
            child.attach(child_pane)

    def detach(self):
        for child in self.children:
            child.detach()
        super().detach()

    def _update_content_width(self, *args):
        self.content_width = max(c.derived_width for c in self.children)

    def _update_content_height(self, *args):
        self.content_height = max(c.derived_height for c in self.children)

    def _update_coords(self, coords: Tuple[float, float, float, float]):
        for child in self.children:
            child.pane.alloc_coords = coords

    def _top_pane(self):
        for child in reversed(self.children):
            if not child.hidden:
                return child.pane

    def on_draw(self):
        for child in self.children:
            child.pane.dispatch_event('on_draw')

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pane = self._top_pane()
        if pane is not None:
            pane.dispatch_event('on_mouse_drag', x, y, dx, dy, buttons,
                                modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        pane = self._top_pane()
        if pane is not None:
            pane.dispatch_event('on_mouse_press', x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        pane = self._top_pane()
        if pane is not None:
            pane.dispatch_event('on_mouse_release', x, y, button, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pane = self._top_pane()
        if pane is not None:
            pane.dispatch_event('on_mouse_scroll', x, y, scroll_x, scroll_y)

    def _observe_mouse_pos(self, pos: Optional[Tuple[float, float]]):
        pane = self._top_pane()
        if pane is not None:
            pane.mouse_pos = pos


class Spacer(View):
    def __init__(self, flex_width=True, flex_height=True, **kwargs):
        super().__init__(flex_width=flex_width,
                         flex_height=flex_height,
                         **kwargs)
