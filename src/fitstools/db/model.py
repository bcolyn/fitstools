def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    cls.__str__ = __str__
    cls.__repr__ = __str__
    return cls


def auto_eq(cls):
    def __eq__(self, other):
        return vars(self).__eq__(vars(other))

    cls.__eq__ = __eq__
    return cls


def auto_init(cls):
    def __init__(self, **kwargs):
        for name in kwargs:
            self.__setattr__(name, kwargs[name])

    cls.__init__ = __init__
    return cls


@auto_str
@auto_eq
@auto_init
class Root:
    path: str
    name: str
    id: int


@auto_str
@auto_eq
@auto_init
class File:
    id: int
    root: Root
    path: str
