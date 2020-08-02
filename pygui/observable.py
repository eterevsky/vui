from typing import Any, Callable, Generic, List, Optional, TypeVar, Union

T = TypeVar('T')


class Observable(Generic[T]):
    """An observable value.

    A object of this class holds a single value. Any number of listeners can be
    registered, that will be called when the value is modified. If `o` is
    an observable value:

    `o.value` is the current value.

    `o.set(val)` will update the value and possibly call the observers.
    The observers *will not be called* if the new value is equal to the old one.

    `o.observe(callback)` registers a callback that will be called every time
    the value is modified. The callbacks are called in the order of
    registration.

    `o.remove_observer(callback_or_object)` unregisters observer(s)
    """
    def __init__(self, value: T):
        """Initializes the observable value.

        Args:
            value: initial value or None by default.
        """
        self.value: T = value
        self._observers: List[Callable[[T], None]] = []

    def set(self, value: T):
        """Updates the value and calls the observers.

        The observers *will not be called* if the new value is equal to
        the old one.
        """
        if self.value != value:
            self.value = value
            for observer in self._observers:
                observer(self.value)

    def observe(self, observer: Callable[[T], None]):
        """Registers an observer callback.

        The callback is added to the end of the queue of observers. When the
        value changes it will be called with its new value as a single argument.
        """
        self._observers.append(observer)

    def remove_observer(self, observer: Any):
        """Unregisers observer callbacks(s).

        Args:
            observer: If it is a function, it will be removed from the list of
              observers directly. If it's an object, any observers that are
              methods of this class will be removed.
        """
        i = 0
        while i < len(self._observers):
            if (self._observers[i] is observer or
                    getattr(self._observers[i], '__self__', None) is observer):
                del self._observers[i]
            else:
                i += 1


MaybeObservable = Union[T, Observable[T]]


def make_observable(x: MaybeObservable[T]) -> Observable[T]:
    """Wrap a value in Observable if it is not Observable.

    When the passed value is already an Observable, return it unchanged.
    """
    return x if isinstance(x, Observable) else Observable(x)


class Attribute(Generic[T]):
    """Defines observable class attributes.

    Used as follows:

        class A(object):
            field = Attribute('field_')

            def __init__(self):
                # Optional. By default will be initialized with
                # Observable(None).
                self.field_ = Observable(0)

        a = A()
        a.field = 100   # sets the value
        print(a.field)  # reads the value
        a.field_.observe(handler)  # adds an observer
        a.field = 200  # will trigger handler
    """
    def __init__(self, observable_name: str):
        """Constructs observable attribute.

        Args:
            observable_name: the name of the field, that contains the underlying
              observable value. It's recommended that it is the name of the
              attribute with appended `_`.
        """
        self.name = observable_name

    def _get_observable(self, instance) -> Observable[T]:
        observable = getattr(instance, self.name, None)
        if observable is None:
            observable = Observable(None)
            setattr(instance, self.name, observable)
        return observable

    def __set__(self, instance, value: T):
        self._get_observable(instance).set(value)

    def __get__(self, instance, owner=None) -> T:
        return self._get_observable(instance).value

