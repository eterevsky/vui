import pyglet.image
from pyglet.image import AbstractImage
from typing import Optional, Tuple, Union

from .view import View, HAlign, VAlign
from .observable import Attribute, MaybeObservable, Observable, make_observable


class Image(View):
    data: Attribute[Optional[AbstractImage]] = Attribute('data_')

    def __init__(self,
                 data: Union[MaybeObservable[Optional[AbstractImage]], str] = None,
                 halign: MaybeObservable[HAlign] = HAlign.CENTER,
                 valign: MaybeObservable[VAlign] = VAlign.CENTER,
                 **kwargs):
        super().__init__(halign=halign, valign=valign, **kwargs)
        if type(data) is str:
            data = pyglet.image.load(data)
        self.data_: Observable[Optional[AbstractImage]] = make_observable(data)
        self.data_.observe(self._update_data)
        self._update_data(self.data)

    def _update_data(self, data):
        self.content_width = data.width
        self.content_height = data.height
        self._texture = data.get_texture(rectangle=True)

    def on_draw(self):
        x0, y0, x1, y1 = self.pane.coords
        self._texture.blit(x0, y0, width=(x1-x0), height=(y1-y0))