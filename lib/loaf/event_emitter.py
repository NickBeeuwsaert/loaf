from collections import defaultdict
from functools import wraps, partial

from .decorator import reify


class fires:
    def __init__(self, *events):
        self.events = events

    def __call__(self, fn):
        @wraps(fn)
        def wrapped_fn(instance, *args, **kwargs):
            result = fn(instance, *args, **kwargs)
            for event in self.events:
                instance.fire(event)
            return result
        return wrapped_fn


class on:
    def __init__(self, *events):
        self.events = events

    def __call__(self, fn):
        try:
            fn._events.update(self.events)
        except AttributeError:
            fn._events = set(self.events)

        return fn


class EventEmitterMeta(type):
    def __init__(cls, name, bases, clsattrs):
        deferred_handlers = set()
        for name, value in clsattrs.items():
            if hasattr(value, '_events'):
                deferred_handlers.update(
                    (event, name)
                    for event in value._events
                )

        # Crawl up the MRO to get all events
        for base in cls.__mro__:
            if hasattr(base, '_deferred_handlers'):
                deferred_handlers.update(base._deferred_handlers)

        cls._deferred_handlers = deferred_handlers
        return super().__init__(name, bases, clsattrs)


class EventEmitter:
    @reify
    def _listeners(self):
        listeners = defaultdict(set)

        # First time _listeners is accessed, add all decorated on handlers
        # for event_type, handler in self._deferred_handlers:
        #     listeners[event_type].add(getattr(self, handler))

        return listeners

    def on(self, event, handler):
        self._listeners[event].add(handler)

    def once(self, event, handler):
        @wraps(handler)
        def once_handler(*args, **kwargs):
            self.remove(event, once_handler)
            return handler(*args, **kwargs)

        self.on(event, once_handler)

    def remove(self, event, handler):
        self._listeners.remove(handler)

    def fire(self, event, *args, **kwargs):
        for handler in self._listeners[event]:
            handler(*args, **kwargs)


# EventEmitter = EventEmitterMeta(
#     'EventEmitter',
#     (EventEmitterBase, ),
#     {'__doc__': EventEmitterBase.__doc__}
# )
