from playhouse.sqlite_ext import *


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in _get_data_dict(self).items())
        )

    cls.__str__ = __str__
    cls.__repr__ = __str__
    return cls


def _get_data_dict(obj):
    if isinstance(obj, Model):
        return obj.__data__
    else:
        return vars(obj)


def auto_eq(cls):
    def __eq__(self, other):
        return _get_data_dict(self).__eq__(_get_data_dict(other))

    cls.__eq__ = __eq__
    return cls


# model notes:
# a file can contain 0 or more images (usually 1)
# an image is always contained by a file
# there are multiple kinds of images (APT_FITS, NINA_FITS, SGP_FITS, ...)

@auto_str
@auto_eq
class Root(Model):
    rowid = RowIDField()
    name = CharField(unique=True)
    last_path = CharField()


@auto_str
@auto_eq
class File(Model):
    rowid = RowIDField()
    root = ForeignKeyField(Root, on_delete='CASCADE')
    path = CharField()
    name = CharField()
    size = IntegerField()
    type = CharField(null=True)  # FITS
    compression = CharField(null=True)  # xz, gz, lz4
    mtime_millis = IntegerField()
    sha1 = BlobField(index=True, null=True)  # or CharField?

    class Meta:
        indexes = (
            (('root', 'path', 'name'), True),  # Note the trailing comma!
        )


@auto_str
@auto_eq
class Image(Model):
    rowid = RowIDField()
    file = ForeignKeyField(File, on_delete='CASCADE', backref='images')


@auto_str
@auto_eq
class ImageMeta(Model):
    image = ForeignKeyField(Image, on_delete='CASCADE', backref='metadata')
    key = CharField()
    value = CharField()

    class Meta:
        indexes = (
            (('image', 'key'), True),  # Note the trailing comma!
        )


CORE_MODELS = [Root, File, Image, ImageMeta]
