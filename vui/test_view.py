import unittest
from unittest.mock import Mock, patch

from .observable import Attribute, Observable, make_observable
from .pane import Pane
from .view import View, HAlign, VAlign


class ViewTest(unittest.TestCase):
    def test_derived_dim(self):
        view = View(min_width=100, flex_height=False)
        self.assertTrue(view.flex_width)
        self.assertFalse(view.flex_height)
        self.assertEqual(view.derived_width, 100)
        self.assertEqual(view.derived_height, 0)
        view.content_width = 50
        view.content_height = 50
        self.assertEqual(view.derived_width, 100)
        self.assertEqual(view.derived_height, 50)
        view.min_width = 200
        self.assertEqual(view.derived_width, 200)

    def test_external_width(self):
        width_ = Observable(100)
        view = View(min_width=width_)
        self.assertEqual(view.derived_width, 100)
        width_.set(200)
        self.assertEqual(view.derived_width, 200)

    def test_background(self):
        view = View(background_color=(1, 2, 3))
        pane = Pane(0, 0, 100, 100)
        view.attach(pane)
        self.assertEqual(pane.background_color, (1, 2, 3))
        view.background_color = (4, 5, 6)
        self.assertEqual(pane.background_color, (4, 5, 6))

    def test_hidden(self):
        class MyView(View):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.calls = 0

            def on_draw(self):
                self.calls += 1

        view = MyView(min_width=100)
        self.assertFalse(view.hidden)
        self.assertEqual(view.derived_width, 100)

        pane = Pane(0, 0, 100, 100)
        view.attach(pane)
        pane.dispatch_event('on_draw')
        self.assertEqual(view.calls, 1)

        view.hidden = True
        self.assertEqual(view.derived_width, 0)
        pane.dispatch_event('on_draw')
        self.assertEqual(view.calls, 1)

    def test_detach(self):
        class MyView(View):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.calls = 0
                self.observe_calls = 0

            def on_draw(self):
                self.calls += 1

            def attach(self, pane):
                super().attach(pane)
                pane.coords_.observe(self.observer)

            def observer(self, coords):
                self.observe_calls += 1

        view = MyView(min_width=100, background_color=(1, 2, 3))
        pane = Pane(0, 0, 100, 100)
        view.attach(pane)
        self.assertEqual(pane.background_color, (1, 2, 3))
        pane.dispatch_event('on_draw')
        self.assertEqual(view.calls, 1)
        self.assertEqual(view.observe_calls, 0)
        pane.coords = (50, 50, 100, 100)
        self.assertEqual(view.observe_calls, 1)

        view.detach()
        self.assertEqual(pane.background_color, None)
        view.background_color = (4, 5, 6)
        self.assertEqual(pane.background_color, None)
        pane.coords = (50, 50, 150, 150)
        self.assertEqual(view.observe_calls, 1)

        pane.dispatch_event('on_draw')
        self.assertEqual(view.calls, 1)

    def test_hfill_vtop(self):
        view = View(min_width=100,
                    min_height=200,
                    halign=HAlign.FILL,
                    valign=VAlign.TOP)
        pane = Pane(0, 0, 500, 600)
        self.assertEqual(pane.coords, (0, 0, 500, 600))
        view.attach(pane)
        self.assertEqual(pane.coords, (0, 400, 500, 600))

        pane.alloc_coords = (100, 100, 600, 500)
        self.assertEqual(pane.coords, (100, 300, 600, 500))

        view.min_height = 300
        self.assertEqual(pane.coords, (100, 200, 600, 500))

    def test_hleft_vcenter(self):
        view = View(min_width=100,
                    min_height=200,
                    halign=HAlign.LEFT,
                    valign=VAlign.CENTER)
        pane = Pane(0, 0, 500, 600)
        self.assertEqual(pane.coords, (0, 0, 500, 600))
        view.attach(pane)
        self.assertEqual(pane.coords, (0, 200, 100, 400))

        pane.alloc_coords = (100, 100, 600, 500)
        self.assertEqual(pane.coords, (100, 200, 200, 400))

        view.min_height = 300
        self.assertEqual(pane.coords, (100, 150, 200, 450))

    def test_hcenter_vfill(self):
        view = View(min_width=100,
                    min_height=200,
                    halign=HAlign.CENTER,
                    valign=VAlign.FILL)
        pane = Pane(0, 0, 500, 600)
        self.assertEqual(pane.coords, (0, 0, 500, 600))
        view.attach(pane)
        self.assertEqual(pane.coords, (200, 0, 300, 600))

        pane.alloc_coords = (100, 100, 600, 500)
        self.assertEqual(pane.coords, (300, 100, 400, 500))

        view.min_width = 300
        self.assertEqual(pane.coords, (200, 100, 500, 500))

    def test_hright_vbottom(self):
        view = View(min_width=100,
                    min_height=200,
                    halign=HAlign.RIGHT,
                    valign=VAlign.BOTTOM)
        pane = Pane(0, 0, 500, 600)
        self.assertEqual(pane.coords, (0, 0, 500, 600))
        view.attach(pane)
        self.assertEqual(pane.coords, (400, 0, 500, 200))

        pane.alloc_coords = (100, 100, 600, 500)
        self.assertEqual(pane.coords, (500, 100, 600, 300))

        view.min_width = 300
        self.assertEqual(pane.coords, (300, 100, 600, 300))

    def test_change_align(self):
        view = View(min_width=100,
                    min_height=200,
                    halign=HAlign.RIGHT,
                    valign=VAlign.BOTTOM)
        pane = Pane(0, 0, 500, 600)
        view.attach(pane)
        self.assertEqual(pane.coords, (400, 0, 500, 200))

        view.halign = HAlign.CENTER
        view.valign = VAlign.FILL
        self.assertEqual(pane.coords, (200, 0, 300, 600))


if __name__ == '__main__':
    unittest.main()