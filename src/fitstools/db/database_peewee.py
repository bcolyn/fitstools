from playhouse.sqlite_ext import *


class Root(Model):
    rowid = RowIDField()
    name = CharField(unique=True)
    last_path = CharField()


class File(Model):
    rowid = RowIDField()
    root = ForeignKeyField(Root, on_delete='CASCADE')
    path = CharField()
    name = CharField()
    size = IntegerField()
    mtime_millis = IntegerField()
    sha1 = BlobField(index=True, null=True)  # or CharField?


class Image(Model):
    rowid = RowIDField()
    file = ForeignKeyField(File, on_delete='CASCADE')

# model notes:
# a file can contain 0 or more images (usually 1)
# an image is always contained by a file
# there are multiple kinds of images (APT_FITS, NINA_FITS, SGP_FITS, ...)
