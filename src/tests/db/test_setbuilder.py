from fitstools.analysis.setbuilder import SetBuilder
from fitstools.db.database_peewee import *

import logging

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def test_combine(database):
    root = Root.create(last_path=r"/dummy/does/not/exist", name="dropbox")
    headers = {
        "IMAGETYP": "LIGHT",
        "CREATOR": "Sequence Generator Pro v3.1.0.479",
        "FILTER": "B",
        "INSTRUME": "ZWO ASI294MC Pro",
        "EXPOSURE": "30",
        "CCD-TEMP": "-17.5",
        "OBJECT": "NGC 1111",
        "XBINNING": "1",
        "YBINNING": "1",
        "GAIN": "120",
        "OFFSET": "30",
        "TELESCOP": "EQMOD ASCOM HEQ5/6",
        "DATE-LOC": "2020-05-30T02:22:49.0968820"
    }
    create_image_with_meta(root, "test1.fit", "test/path", headers)
    create_image_with_meta(root, "test2.fit", "test/path",
                           {**headers, "FILTER": "R", "DATE-LOC": "2020-05-30T02:24:05"})
    create_image_with_meta(root, "test3.fit", "test/path",
                           {**headers, "FILTER": "R", "DATE-LOC": "2020-05-30T02:26:10"})
    assert SetBuilder.combine() == (3, 2)


def create_image_with_meta(root, name, path, meta):
    file = File.create(name=name, path=path, root=root, size=123456, mtime_millis=0)
    image = Image.create(file=file)
    for (key, value) in meta.items():
        ImageMeta.create(image=image, key=key, value=value)
