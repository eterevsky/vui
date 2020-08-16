from enum import Enum
from typing import Optional, Tuple, Union

from .pane import Pane, DUMMY_PANE
from . import event
from .observable import Attribute, MaybeObservable, Observable, make_observable


class HAlign(Enum):
    """Horizontal alignment of a pane within owning pane.

    This enum determines how the pane controlled by a given View will be located
    within a possibly larger pane allocated by the parent layout. If the value
    is one of LEFT, CENTER, RIGHT, the pane will have the width equal to
    `View.derived_width`. For FILL, the pane will fill the full width allocated
    by the parent layout.
    """
    # 0 reserved for DEFAULT in case it is useful.
    LEFT = 1
    CENTER = 2
    RIGHT = 3
    FILL = 4


class VAlign(Enum):
    """Vertical alignment of a pane within owning pane.

    Similar to `HAlign` but for vertical space.
    """
    # 0 reserved for DEFAULT in case it is useful.
    BOTTOM = 1
    CENTER = 2
    TOP = 3
    FILL = 4


def _calc_coords(lo: float, hi: float, dim: float, align: Union[HAlign, VAlign]):
    extra = hi - lo - dim
    # print('_calc_coords lo={} hi={} dim={} align={} extra={}'.format(lo, hi, dim, align, extra))
    if align.value == 4 or extra <= 0:
        # If FILL or the space is too small, we just take all the available
        # space.
        return lo, hi
    if align.value == 1:
        return lo, lo + dim
    if align.value == 2:
        l = lo + extra / 2
        return l, l + dim
    if align.value == 3:
        return hi - dim, hi
    raise ValueError("Unexpected alignment: {}".format(align))


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
      flex_width, flex_height: boolean attributes, set by the user code. These
        attributes determine how the parent layout will allocate space to it.
        When False, the layout will attempt to allocate exactly `derived_*`
        space. Otherwise, it might allocate extra space. This is orthogonal
        to whether halign/valign is set to FILL. Setting flex_width to True
        and halign to CENTER will result in allocating to the view of a bigger
        area, but it still rendering in a smaller active area of exactly
        `derived_width`.
      halign, valign: attributes determine how the view should behave if its
        content is smaller than the allocated space. Based on these values
        the view will set `coords` in the attached pane.
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
    halign: Attribute[HAlign] = Attribute('halign_')
    valign: Attribute[VAlign] = Attribute('valign_')
    hidden: Attribute[bool] = Attribute('hidden_')
    background_color: Attribute[Optional[Tuple[int, int, int]]] = Attribute(
        'background_color_')

    def __init__(self, min_width: MaybeObservable[Optional[float]] = None,
                 min_height: MaybeObservable[Optional[float]] = None,
                 flex_width: MaybeObservable[bool] = True,
                 flex_height: MaybeObservable[bool] = True,
                 halign: MaybeObservable[HAlign] = HAlign.FILL,
                 valign: MaybeObservable[VAlign] = VAlign.FILL,
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
        self.min_height_.observe(self._calc_height)
        self.content_width_.observe(self._calc_width)
        self.content_height_.observe(self._calc_height)
        self.derived_width_: Observable[float] = Observable(0)
        self.derived_height_: Observable[float] = Observable(0)
        self.derived_width_.observe(self._update_pane)
        self.derived_height_.observe(self._update_pane)

        self.flex_width_: Observable[bool] = make_observable(flex_width)
        self.flex_height_: Observable[bool] = make_observable(flex_height)

        self.halign_: Observable[HAlign] = make_observable(halign)
        self.valign_: Observable[VAlign] = make_observable(valign)
        self.halign_.observe(self._update_pane)
        self.valign_.observe(self._update_pane)

        self.background_color_: Observable[Optional[Tuple[
            int, int, int]]] = make_observable(background_color)
        self.hidden_: Observable[bool] = make_observable(hidden)
        self.hidden_.observe(self._calc_width)
        self.hidden_.observe(self._calc_height)

        self._calc_width()
        self._calc_height()

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
            pane.push_handlers(self)
            pane.push_handlers(on_draw=self.on_draw_check_hidden)
            pane.swap_background(self.background_color_)
            pane.alloc_coords_.observe(self._update_pane)
            self._update_pane()

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
        self.derived_width_.remove_observer(observer)
        self.derived_height_.remove_observer(observer)
        self.flex_width_.remove_observer(observer)
        self.flex_height_.remove_observer(observer)
        self.halign_.remove_observer(observer)
        self.valign_.remove_observer(observer)
        self.background_color_.remove_observer(observer)
        self.hidden_.remove_observer(observer)

    def _update_pane(self, *args):
        """Sets active pane coords."""
        if self.pane is None:
            return
        ox0, oy0, ox1, oy1 = self.pane.alloc_coords
        x0, x1 = _calc_coords(ox0, ox1, self.derived_width, self.halign)
        y0, y1 = _calc_coords(oy0, oy1, self.derived_height, self.valign)
        self.pane.coords = (x0, y0, x1, y1)

    def on_mouse_enter(self, *args):
        self.pane.window.set_mouse_cursor(None)

    @event.priority(2)
    def on_draw_check_hidden(self):
        if self.hidden:
            return event.EVENT_HANDLED

    def _calc_width(self, *args):
        if self.hidden:
            self.derived_width = 0
        elif self.min_width is None:
            if self.content_width is None:
                self.derived_width = 0
            else:
                self.derived_width = self.content_width
        else:
            self.derived_width = self.min_width

    def _calc_height(self, *args):
        if self.hidden:
            self.derived_height = 0
        elif self.min_height is None:
            if self.content_height is None:
                self.derived_height = 0
            else:
                self.derived_height = self.content_height
        else:
            self.derived_height = self.min_height
