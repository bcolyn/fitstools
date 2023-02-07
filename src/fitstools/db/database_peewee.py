import gzip
import lzma
import os.path
import typing

from astropy.io.fits import Header
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


# model notes:
# a file can contain 0 or more images (usually 1)
# an image is always contained by a file
# there are multiple kinds of images (APT_FITS, NINA_FITS, SGP_FITS, ...)
# an image has metadata in its header fields
# images group together in a set - a set of images is taken at roughly the same time, same material, same target
# an image can have statistics - median, fwhm/hfr, noise evaluation, number of stars

@auto_str
class Root(Model):
    rowid = RowIDField()
    name = CharField(unique=True)
    last_path = CharField()

    def __eq__(self, other):
        return self.name == other.name and self.last_path == other.last_path


@auto_str
class File(Model):
    rowid = RowIDField()
    root = ForeignKeyField(Root, on_delete='CASCADE')
    path = CharField()
    name = CharField()
    size = IntegerField()
    # type = CharField(index=True, null=True)  # FITS
    # compression = CharField(null=True)  # xz, gz, lz4
    mtime_millis = IntegerField()

    # sha1 = BlobField(index=True, null=True)  # or CharField?

    class Meta:
        indexes = (
            (('root', 'path', 'name'), True),  # Note the trailing comma!
        )

    def get_file_exts(self) -> typing.List[str]:
        parts = str(self.name).lower().rsplit('.', maxsplit=2)
        if len(parts) and parts[0] == '':  # hidden file that starts with a '.'
            parts = parts[1:]
        if len(parts) == 1:  # no ext
            return []
        ext = parts[-1]
        if ext == "xz" or ext == "gz":  # is compressed?
            return parts[-2:]
        else:
            return parts[-1:]

    def full_filename(self) -> str:
        return os.path.join(str(self.root.last_path), str(self.path), str(self.name))

    def fopen(self):
        file_exts = self.get_file_exts()
        if len(file_exts) and file_exts[-1] == "xz":
            return lzma.open(self.full_filename(), mode='rb')
        elif len(file_exts) and file_exts[-1] == "gz":
            return gzip.open(self.full_filename(), mode='rb')
        else:
            return open(self.full_filename(), mode='rb')


# @auto_str
# class FileMeta(Model):
#     file = ForeignKeyField(File, on_delete='CASCADE', backref='metadata')
#     key = CharField()
#     value = CharField()
#
#     class Meta:
#         indexes = (
#             (('file', 'key', 'value'), False),  # Note the trailing comma!
#         )

@auto_str
class ImageSet(Model):
    root = ForeignKeyField(Root, on_delete='CASCADE')
    path = CharField()
    img_type = CharField()
    exposure = FloatField()
    camera_temperature = IntegerField(null=True)
    camera_name = CharField(null=True)
    object_name = CharField()
    filter = CharField(null=True)
    xbin = IntegerField(null=True)
    ybin = IntegerField(null=True)
    gain = IntegerField(null=True)
    offset = IntegerField(null=True)
    telescope = CharField(null=True)
    capture_date = DateField()


@auto_str
class Image(Model):
    rowid = RowIDField()
    file = ForeignKeyField(File, on_delete='CASCADE', backref='images', null=False)
    image_set = ForeignKeyField(File, on_delete='SET NULL', backref='images', null=True)

    def get_header(self) -> Header:
        meta_dict = {meta.key: meta.value for meta in self.metadata}
        return Header(meta_dict)


@auto_str
class ImageMeta(Model):
    image = ForeignKeyField(Image, on_delete='CASCADE', backref='metadata')
    key = CharField()
    value = CharField()

    class Meta:
        indexes = (
            (('key', 'value'), False),  # Note the trailing comma!
        )


CORE_MODELS = [Root, File, Image, ImageMeta, ImageSet]
