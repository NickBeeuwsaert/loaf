from collections import defaultdict
from functools import wraps, partial, update_wrapper

from .decorator import reify


class emit:
    def __init__(self, event):
        self.event = event

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(inst, *args, **kwargs):
            result = fn(inst, *args, **kwargs)
            inst.emit(self.event)
            return result
        return wrapper


class EventEmitter:
    @reify
    def _listeners(self):
        return defaultdict(set)

    def on(self, event, handler=None):
        if handler is None:
            return partial(self.on, event)
        self._listeners[event].add(handler)

    def once(self, event, handler):
        @wraps(handler)
        def once_handler(*args, **kwargs):
            self.remove(event, once_handler)
            return handler(*args, **kwargs)

        self.on(event, once_handler)

    def remove(self, event, handler):
        self._listeners.remove(handler)

    def emit(self, event, *args, **kwargs):
        for handler in self._listeners[event]:
            handler(*args, **kwargs)
