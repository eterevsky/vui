import enum
import pyglet    # type: ignore
from typing import List, Optional, Tuple, Union

from .event import EVENT_HANDLED, EVENT_UNHANDLED
from .observable import Attribute, Observable
from .pane import Pane
from .view import View


class RootLayout(object):
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
    def child(self) -> View:
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
        self.child_pane.coords = (0, 0, width, height)


class Orientation(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class StackLayout(View):
    def __init__(self, orientation: Orientation, *children: List[View],
                 **kwargs):
        super().__init__(**kwargs)

        self.orientation = orientation
        self._mouseover_pane = None
        self._dragging_pane = None
        self._dragging_button = 0

        self.children = children
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

        x0, y0, x1, y1 = self.pane.coords
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

    def _find_child_pane(self, x, y) -> Pane:
        """Returns the child contining (x, y) or None."""
        if (self._mouseover_pane is not None
                and self._mouseover_pane.contains(x, y)):
            return self._mouseover_pane
        for child in self.children:
            if child.pane.contains(x, y):
                return child.pane
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

    def _update(self):
        x0, y0, x1, y1 = self.pane.coords
        width = x1 - x0

        count_flex = sum(child.flex_width for child in self.children)
        extra = (width - self.derived_width) / max(count_flex, 1)

        x = x0
        for child in self.children:
            if extra <= 0 or not child.flex_width:
                next_x = min(x + child.derived_width, x1)
            else:
                next_x = x + child.derived_width + extra
            child.pane.coords = (x, y0, next_x, y1)
            x = next_x


class VStackLayout(StackLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(Orientation.VERTICAL, *args, **kwargs)

    def _calc_content_width(self):
        return max(c.derived_width for c in self.children)

    def _calc_content_height(self):
        return sum(c.derived_height for c in self.children)

    def _update(self):
        x0, y0, x1, y1 = self.pane.coords
        height = y1 - y0

        count_flex = sum(child.flex_height for child in self.children)
        extra = (height - self.derived_height) / max(count_flex, 1)

        y = y1
        for child in self.children:
            if extra <= 0 or not child.flex_height:
                next_y = max(y - child.derived_height, y0)
            else:
                next_y = y - child.derived_height - extra
            child.pane.coords = (x0, next_y, x1, y)
            y = next_y


class LayersLayout(View):
    def __init__(self, *children, **kwargs):
        super().__init__(**kwargs)

        self.children = children

        if not self.min_width_set():
            self.set_min_width(max(c.min_width for c in self.children))
        if not self.min_height_set():
            self.set_min_height(max(c.min_height for c in self.children))
        if not self.flex_width_set():
            self.set_flex_width(any(c.flex_width for c in self.children))
        if not self.flex_height_set():
            self.set_flex_width(any(c.flex_height for c in self.children))

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
        x0, y0, x1, y1 = self.pane.x0, self.pane.y0, self.pane.x1, self.pane.y1
        for child in self.children:
            child_pane = Pane(pane.window, x0, y0, x1, y1)
            child.attach(child_pane)
            pane.push_handlers(self.on_content_resize)

    def detach(self):
        super().detach()
        for child in self.children:
            child.pane.remove_handlers(self)
            child.detach()

    def on_draw(self):
        for child in self.children:
            child.pane.dispatch_event('on_draw')

    def on_mouse_enter(self, x, y):
        for child in reversed(self.children):
            if (child.pane.dispatch_event('on_mouse_enter', x, y) is
                    EVENT_HANDLED):
                break

    def on_mouse_leave(self, x, y):
        for child in reversed(self.children):
            if (child.pane.dispatch_event('on_mouse_leave', x, y) is
                    EVENT_HANDLED):
                break

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        for child in reversed(self.children):
            if (child.pane.dispatch_event('on_mouse_drag', x, y, dx, dy,
                                          buttons, modifiers) is
                    EVENT_HANDLED):
                break

    def on_mouse_motion(self, x, y, dx, dy):
        for child in reversed(self.children):
            if (child.pane.dispatch_event('on_mouse_motion', x, y, dx, dy) is
                    EVENT_HANDLED):
                break

    def on_mouse_press(self, x, y, button, modifiers):
        for child in reversed(self.children):
            if (child.pane.dispatch_event('on_mouse_press', x, y, button,
                                          modifiers) is EVENT_HANDLED):
                break

    def on_mouse_release(self, x, y, button, modifiers):
        for child in reversed(self.children):
            if (child.pane.dispatch_event('on_mouse_release', x, y, button,
                                          modifiers) is EVENT_HANDLED):
                break

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for child in reversed(self.children):
            if (child.pane.dispatch_event('on_mouse_scroll', x, y, scroll_x,
                                          scroll_y) is EVENT_HANDLED):
                break

    def on_dims_change(self, *args):
        self._resize()

    def on_content_resize(self):
        self._resize()

    def _resize(self):
        for child in self.children:
            child.pane.change_dims(x0=self.pane.x0, x1=self.pane.x1,
                                   y0=self.pane.y0, y1=self.pane.y1)


class Spacer(View):
    def __init__(self, flex_width=True, flex_height=True, **kwargs):
        super().__init__(flex_width=flex_width, flex_height=flex_height,
                         **kwargs)
