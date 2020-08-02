import unittest
from unittest.mock import Mock

from .observable import Attribute, Observable, make_observable


class ObservableTest(unittest.TestCase):
    def test_observe(self):
        v = Observable(1)
        callback1 = Mock()
        callback2 = Mock()
        v.observe(callback1)
        v.observe(callback2)
        v.set(1)
        callback1.assert_not_called()
        callback2.assert_not_called()
        v.set(2)
        callback1.assert_called_once_with(2)
        callback2.assert_called_once_with(2)

    def test_remove(self):
        called = 0

        # Remove doesn't work well with mocks, since they aren't detected as
        # equal.
        def observer(v):
            nonlocal called
            called += 1

        v = Observable(1)
        v.observe(observer)
        v.set(2)
        self.assertEqual(called, 1)
        v.remove_observer(observer)
        v.set(3)
        self.assertEqual(called, 1)


class AttributeTest(unittest.TestCase):
    def test_get_set_observe(self):
        class A(object):
            x = Attribute('x_')
            def __init__(self):
                self.x_ = Observable(0)

        a = A()
        self.assertEqual(a.x, 0)
        a.x = 1
        self.assertEqual(a.x, 1)

        callback = Mock()
        a.x_.observe(callback)
        a.x = 2
        callback.assert_called_once_with(2)

    def test_init_none(self):
        # pylint: disable=no-member
        class A(object):
            x = Attribute('x_')

        a = A()
        self.assertEqual(a.x, None)
        a.x = 1
        self.assertEqual(a.x, 1)

        callback = Mock()
        a.x_.observe(callback)
        a.x = 2
        callback.assert_called_once_with(2)

    def test_ext_observable(self):
        class A(object):
            x = Attribute('x_')
            def __init__(self, value):
                self.x_ = make_observable(value)

        v = Observable(0)
        callback = Mock()
        v.observe(callback)

        a = A(v)
        callback.assert_not_called()
        self.assertEqual(a.x, 0)
        a.x = 1
        self.assertEqual(a.x, 1)
        callback.assert_called_once_with(1)

    def test_make_observable(self):
        class A(object):
            x = Attribute('x_')
            def __init__(self, value):
                self.x_ = make_observable(value)

        a = A(0)
        self.assertEqual(a.x, 0)
        a.x = 1
        self.assertEqual(a.x, 1)

        callback = Mock()
        a.x_.observe(callback)
        a.x = 2
        callback.assert_called_once_with(2)


if __name__ == '__main__':
    unittest.main()