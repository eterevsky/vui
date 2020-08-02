from typing import Optional, Tuple

from .pane import Pane, DUMMY_PANE
from . import event
from .observable import Attribute, MaybeObservable, Observable, make_observable


class View(object):
    """A class that renders a UI element in a given pane.

    This is an abstract class that can be implemented by all the UI widgets. It
    manages the attributes that determine the size of the pane that will be
    created by the parent layout view.

    Attributes:
      min_width, min_height: set by the external code that creates the View,
        those are the minimal dimensions of the view. These attributes take
        precendence over content_width and content_height. By default are
        set to None. When these attributes are None, they are ignored and
        content_width and content_height is used instead.
      content_width, content_height: have the same effect as min_*, but with
        lower priority (if min_width is set, content_width is generally
        ignored). Unlike min_*, these attributes are set *by the class itself*.
      derived_width, derived_height: managed by the class, equal
        to min_width/min_height if it's defined, otherwise to
        content_width/content_height.
      flex_width, flex_height: boolean attributes, set by the external code. If
        one of these attributes is set to False, the widget requires to be have
        exactly derived_* size in a specified dimension. Otherwise,
        the underlying pane will be resized
      hidden: boolean attribute, set by the external code. If True, will not
        render anything in on_draw.
      background_color: same as background_color in underlying Pane.
    """
    min_width: Attribute[Optional[float]] = Attribute('min_width_')
    min_height: Attribute[Optional[float]] = Attribute('min_height_')
    content_width: Attribute[Optional[float]] = Attribute('content_width_')
    content_height: Attribute[Optional[float]] = Attribute('content_height_')
    derived_width: Attribute[float] = Attribute('derived_width_')
    derived_height: Attribute[float] = Attribute('derived_height_')
    flex_width: Attribute[bool] = Attribute('flex_width_')
    flex_height: Attribute[bool] = Attribute('flex_height_')
    hidden: Attribute[bool] = Attribute('hidden_')
    background_color: Attribute[Optional[Tuple[int, int, int]]] = Attribute(
        'background_color_')

    def __init__(self, min_width: MaybeObservable[Optional[float]] = None,
                 min_height: MaybeObservable[Optional[float]] = None,
                 flex_width: MaybeObservable[bool] = False,
                 flex_height: MaybeObservable[bool] = False,
                 background_color:
                    MaybeObservable[Optional[Tuple[int, int, int]]] = None,
                 hidden: MaybeObservable[bool] = False):
        self.pane: Optional[Pane] = None
        self.min_width_: Observable[Optional[float]] = make_observable(
            min_width)
        self.min_height_: Observable[Optional[float]] = make_observable(
            min_height)
        self.content_width_: Observable[Optional[float]] = Observable(None)
        self.content_height_: Observable[Optional[float]] = Observable(None)

        self.min_width_.observe(self._calc_width)
        self.content_width_.observe(self._calc_width)
        self.min_height_.observe(self._calc_height)
        self.content_height_.observe(self._calc_height)

        self.flex_width_: Observable[bool] = make_observable(flex_width)
        self.flex_height_: Observable[bool] = make_observable(flex_height)

        self.background_color_: Observable[Optional[Tuple[
            int, int, int]]] = make_observable(background_color)
        self.hidden_: Observable[bool] = make_observable(hidden)
        self.hidden_.observe(self._calc_width)
        self.hidden_.observe(self._calc_height)

        self.derived_width_: Observable[float] = Observable(0)
        self.derived_height_: Observable[float] = Observable(0)
        self._calc_width(None)
        self._calc_height(None)

    def __str__(self):
        return '{}[{}]{}'.format(self.__class__.__name__, self.pane,
                                 '[hidden]' if self.hidden else '')

    def attach(self, pane: Pane):
        """Attach the view to a pane.

        Usually called by the parent layout class.
        """
        self.detach()
        self.pane = pane
        if pane is not None:
            self.pane.push_handlers(self)
            self.pane.push_handlers(on_draw=self.on_draw_check_hidden)
            self.pane.swap_background(self.background_color_)

    def detach(self):
        if self.pane is None:
            return
        self.pane.remove_handlers(self)
        self.pane.remove_observer(self)
        self.pane.swap_background(None)

    def remove_observer(self, observer):
        self.min_width_.remove_observer(observer)
        self.min_height_.remove_observer(observer)
        self.content_width_.remove_observer(observer)
        self.content_height_.remove_observer(observer)
        self.min_width_.remove_observer(observer)
        self.content_width_.remove_observer(observer)
        self.min_height_.remove_observer(observer)
        self.content_height_.remove_observer(observer)
        self.flex_width_.remove_observer(observer)
        self.flex_height_.remove_observer(observer)
        self.background_color_.remove_observer(observer)
        self.hidden_.remove_observer(observer)
        self.derived_width_.remove_observer(observer)
        self.derived_height_.remove_observer(observer)

    def on_mouse_enter(self, *args):
        self.pane.window.set_mouse_cursor(None)

    @event.priority(2)
    def on_draw_check_hidden(self):
        if self.hidden:
            return event.EVENT_HANDLED

    def _calc_width(self, _):
        if self.hidden:
            self.derived_width = 0
        elif self.min_width is None:
            if self.content_width is None:
                self.derived_width = 0
            else:
                self.derived_width = self.content_width
        else:
            self.derived_width = self.min_width

    def _calc_height(self, _):
        if self.hidden:
            self.derived_height = 0
        elif self.min_height is None:
            if self.content_height is None:
                self.derived_height = 0
            else:
                self.derived_height = self.content_height
        else:
            self.derived_height = self.min_height
