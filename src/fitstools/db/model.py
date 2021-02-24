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


@auto_str
@auto_eq
class Root:
    def __init__(self, id, name, path):
        self.id = id
        self.name = name
        self.path = path

    @staticmethod
    def from_row(row):
        return Root(row['id'], row['name'], row['path'])
