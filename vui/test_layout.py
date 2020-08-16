import unittest
from unittest.mock import Mock, patch

from .layout import RootLayout, HStackLayout, VStackLayout, LayersLayout
from .observable import Attribute, Observable, make_observable
from .pane import Pane
from .view import View, HAlign, VAlign


class MyView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_draw_calls = 0

    def on_draw(self):
        self.on_draw_calls += 1


class RootLayoutTest(unittest.TestCase):
    def test_init_root(self):
        window = Mock()
        window.width = 200
        window.height = 100
        view = MyView(background_color=(1, 2, 3))

        layout = RootLayout(window, view)
        self.assertEqual(layout.child_pane.background_color, (1, 2, 3))
        layout.on_draw()

        self.assertEqual(view.on_draw_calls, 1)

        other_view = View()
        layout.child = other_view

        self.assertEqual(layout.child_pane.background_color, None)
        layout.on_draw()
        self.assertEqual(view.on_draw_calls, 1)

    def test_mouseover(self):
        window = Mock()
        window.width = 200
        window.height = 100
        layout = RootLayout(window)

        callback = Mock()
        layout.child_pane.mouse_pos_.observe(callback)
        self.assertEqual(layout.child_pane.mouse_pos, None)

        layout.on_mouse_leave(1, 2)
        callback.assert_not_called()
        self.assertEqual(layout.child_pane.mouse_pos, None)

        layout.on_mouse_enter(50, 50)
        callback.assert_called_once_with((50, 50))
        callback.reset_mock()
        self.assertEqual(layout.child_pane.mouse_pos, (50, 50))

        layout.on_mouse_motion(51, 51, 1, 1)
        callback.assert_called_once_with((51, 51))
        callback.reset_mock()
        self.assertEqual(layout.child_pane.mouse_pos, (51, 51))


class FakeView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_draw_calls = 0
        self.on_mouse_press_calls = 0

    def on_draw(self, *args):
        self.on_draw_calls += 1

    def on_mouse_press(self, *args):
        self.on_mouse_press_calls += 1


class HStackLayoutTest(unittest.TestCase):
    def setUp(self):
        self.child1 = FakeView(min_height=100,
                               flex_height=True,
                               min_width=200,
                               flex_width=True,
                               halign=HAlign.CENTER,
                               valign=VAlign.CENTER)
        self.child2 = FakeView(min_height=150,
                               flex_height=False,
                               min_width=100,
                               flex_width=False,
                               valign=VAlign.TOP)
        self.child3 = FakeView(min_height=200,
                               flex_height=False,
                               min_width=100,
                               flex_width=True,
                               halign=HAlign.FILL,
                               valign=VAlign.FILL,
                               hidden=True)
        self.stack = HStackLayout(self.child1, self.child2, self.child3)
        self.pane = Pane(100, 150, 600, 550)
        self.stack.attach(self.pane)

    def test_dims(self):
        self.assertEqual(self.stack.min_width, None)
        self.assertEqual(self.stack.min_height, None)
        self.assertEqual(self.stack.derived_width, 300)
        self.assertEqual(self.stack.derived_height, 150)
        self.assertFalse(self.stack.hidden)

    def test_child_alloc_coords(self):
        self.assertEqual(self.child1.pane.alloc_coords, (100, 150, 500, 550))
        self.assertEqual(self.child2.pane.alloc_coords, (500, 150, 600, 550))

    def test_hide(self):
        self.child2.hidden = True
        self.assertEqual(self.child1.pane.alloc_coords, (100, 150, 600, 550))

    def test_reveal(self):
        self.child3.hidden = False
        self.assertEqual(self.child1.pane.alloc_coords, (100, 150, 350, 550))
        self.assertEqual(self.child2.pane.alloc_coords, (350, 150, 450, 550))
        self.assertEqual(self.child3.pane.alloc_coords, (450, 150, 600, 550))

    def test_child_coords(self):
        self.child3.hidden = False
        self.assertEqual(self.child1.pane.coords, (125, 300, 325, 400))
        self.assertEqual(self.child2.pane.coords, (350, 400, 450, 550))
        self.assertEqual(self.child3.pane.coords, (450, 150, 600, 550))

    def test_draw(self):
        self.pane.dispatch_event('on_draw')
        self.assertEqual(self.child1.on_draw_calls, 1)
        self.assertEqual(self.child2.on_draw_calls, 1)
        self.assertEqual(self.child3.on_draw_calls, 0)

    def test_mouse_press(self):
        self.child3.hidden = False

        self.pane.dispatch_event('on_mouse_press', 200, 350, None, None)
        self.assertEqual(self.child1.on_mouse_press_calls, 1)
        self.assertEqual(self.child2.on_mouse_press_calls, 0)
        self.assertEqual(self.child3.on_mouse_press_calls, 0)

        self.pane.dispatch_event('on_mouse_press', 500, 350, None, None)
        self.assertEqual(self.child1.on_mouse_press_calls, 1)
        self.assertEqual(self.child2.on_mouse_press_calls, 0)
        self.assertEqual(self.child3.on_mouse_press_calls, 1)

        # Outside of the active area of a child pane.
        self.pane.dispatch_event('on_mouse_press', 110, 350, None, None)
        self.assertEqual(self.child1.on_mouse_press_calls, 1)
        self.assertEqual(self.child2.on_mouse_press_calls, 0)
        self.assertEqual(self.child3.on_mouse_press_calls, 1)

        self.pane.dispatch_event('on_mouse_press', 200, 200, None, None)
        self.assertEqual(self.child1.on_mouse_press_calls, 1)
        self.assertEqual(self.child2.on_mouse_press_calls, 0)
        self.assertEqual(self.child3.on_mouse_press_calls, 1)


class VStackLayoutTest(unittest.TestCase):
    def test_v2views(self):
        child1 = FakeView(min_height=100,
                          flex_height=True,
                          min_width=200,
                          flex_width=True)
        child2 = FakeView(min_height=150,
                          flex_height=False,
                          min_width=100,
                          flex_width=False)
        stack = VStackLayout(child1, child2)
        self.assertEqual(stack.min_width, None)
        self.assertEqual(stack.min_height, None)
        self.assertEqual(stack.derived_width, 200)
        self.assertEqual(stack.derived_height, 250)
        self.assertFalse(stack.hidden)
        pane = Pane(100, 150, 500, 550)
        stack.attach(pane)

        self.assertEqual(child1.pane.alloc_coords, (100, 300, 500, 550))
        self.assertEqual(child2.pane.alloc_coords, (100, 150, 500, 300))

    def test_horizontal_overflow(self):
        child1 = FakeView(min_height=100,
                          flex_height=True,
                          min_width=200,
                          flex_width=True)
        child2 = FakeView(min_height=150,
                          flex_height=False,
                          min_width=100,
                          flex_width=False)
        stack = HStackLayout(child1, child2)
        pane = Pane(0, 0, 250, 100)
        stack.attach(pane)

        self.assertEqual(child1.pane.alloc_coords, (0, 0, 200, 100))
        self.assertEqual(child2.pane.alloc_coords, (200, 0, 250, 100))


class LayersLayoutTest(unittest.TestCase):
    def setUp(self):
        self.child1 = FakeView(min_height=100,
                               flex_height=True,
                               min_width=200,
                               flex_width=True,
                               valign=VAlign.FILL,
                               halign=HAlign.FILL)
        self.child2 = FakeView(min_height=150,
                               flex_height=False,
                               min_width=100,
                               flex_width=False,
                               valign=VAlign.CENTER,
                               halign=HAlign.CENTER)
        self.child3 = FakeView(min_height=150,
                               flex_height=False,
                               min_width=100,
                               flex_width=False,
                               hidden=True)
        self.layers = LayersLayout(self.child1, self.child2)
        self.pane = Pane(100, 150, 500, 550)
        self.layers.attach(self.pane)

    def test_dims(self):
        self.assertEqual(self.layers.min_width, None)
        self.assertEqual(self.layers.min_height, None)
        self.assertEqual(self.layers.derived_width, 200)
        self.assertEqual(self.layers.derived_height, 150)
        self.assertFalse(self.layers.hidden)

    def test_coords(self):
        self.assertEqual(self.child1.pane.coords, (100, 150, 500, 550))
        self.assertEqual(self.child2.pane.coords, (250, 275, 350, 425))

    def test_mouse_pos(self):
        self.pane.mouse_pos = (300, 300)
        self.assertEqual(self.child1.pane.mouse_pos, None)
        self.assertEqual(self.child2.pane.mouse_pos, (300, 300))

        self.pane.mouse_pos = (200, 200)
        self.assertEqual(self.child1.pane.mouse_pos, (200, 200))
        self.assertEqual(self.child2.pane.mouse_pos, None)

    def test_on_draw(self):
        self.pane.dispatch_event('on_draw')
        self.assertEqual(self.child1.on_draw_calls, 1)
        self.assertEqual(self.child2.on_draw_calls, 1)
        self.assertEqual(self.child3.on_draw_calls, 0)

    def test_on_mouse_press(self):
        self.pane.dispatch_event('on_mouse_press', 300, 300, 1, 0)
        self.assertEqual(self.child1.on_mouse_press_calls, 0)
        self.assertEqual(self.child2.on_mouse_press_calls, 1)
        self.assertEqual(self.child3.on_mouse_press_calls, 0)

        # Not covered by child2
        self.pane.dispatch_event('on_mouse_press', 200, 200, 1, 0)
        self.assertEqual(self.child1.on_mouse_press_calls, 1)
        self.assertEqual(self.child2.on_mouse_press_calls, 1)
        self.assertEqual(self.child3.on_mouse_press_calls, 0)


if __name__ == '__main__':
    unittest.main()
