class reify:
    """Acts similar to a property, except the result will be
    set as an attribute on the instance instead of recomputed
    each access
    inspired by pyramids `pyramid.decorators.reify` decorator
    """

    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, owner):
        if instance is None:
            return self

        fn = self.fn
        val = fn(instance)

        setattr(instance, fn.__name__, val)

        return val
