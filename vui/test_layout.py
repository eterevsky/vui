import unittest
from unittest.mock import Mock, patch

from .layout import RootLayout, HStackLayout, VStackLayout
from .observable import Attribute, Observable, make_observable
from .pane import Pane
from .view import View


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
        self.on_mouse_drag_calls = []
        self.on_mouse_press_calls = []
        self.on_mouse_release_calls = []
        self.on_mouse_scroll_calls = []


class StackLayoutTest(unittest.TestCase):
    def test_h2views(self):
        child1 = FakeView(min_height=100, flex_height=True, min_width=200,
                          flex_width=True)
        child2 = FakeView(min_height=150, flex_height=False, min_width=100,
                          flex_width=False)
        stack = HStackLayout(child1, child2)
        self.assertEqual(stack.min_width, None)
        self.assertEqual(stack.min_height, None)
        self.assertEqual(stack.derived_width, 300)
        self.assertEqual(stack.derived_height, 150)
        self.assertFalse(stack.hidden)
        pane = Pane(100, 150, 500, 550)
        stack.attach(pane)

        x0, y0, x1, y1 = child1.pane.coords
        self.assertEqual(x0, 100)
        self.assertEqual(y0, 150)
        self.assertEqual(x1, 400)
        self.assertEqual(y1, 550)

        x0, y0, x1, y1 = child2.pane.coords
        self.assertEqual(x0, 400)
        self.assertEqual(y0, 150)
        self.assertEqual(x1, 500)
        self.assertEqual(y1, 550)

    def test_v2views(self):
        child1 = FakeView(min_height=100, flex_height=True, min_width=200,
                          flex_width=True)
        child2 = FakeView(min_height=150, flex_height=False, min_width=100,
                          flex_width=False)
        stack = VStackLayout(child1, child2)
        self.assertEqual(stack.min_width, None)
        self.assertEqual(stack.min_height, None)
        self.assertEqual(stack.derived_width, 200)
        self.assertEqual(stack.derived_height, 250)
        self.assertFalse(stack.hidden)
        pane = Pane(100, 150, 500, 550)
        stack.attach(pane)

        x0, y0, x1, y1 = child1.pane.coords
        self.assertEqual(x0, 100)
        self.assertEqual(y0, 300)
        self.assertEqual(x1, 500)
        self.assertEqual(y1, 550)

        x0, y0, x1, y1 = child2.pane.coords
        self.assertEqual(x0, 100)
        self.assertEqual(y0, 150)
        self.assertEqual(x1, 500)
        self.assertEqual(y1, 300)


if __name__ == '__main__':
    unittest.main()
