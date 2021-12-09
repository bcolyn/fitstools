import pytest
from fs.memoryfs import MemoryFS
from peewee import SqliteDatabase

from fitstools.db.database_peewee import CORE_MODELS


@pytest.fixture
def database():
    db = SqliteDatabase(':memory:', pragmas={
        'journal_mode': 'wal',
        'cache_size': -1 * 64000,  # 64MB
        'foreign_keys': 1
    })

    db.bind(CORE_MODELS, bind_refs=False, bind_backrefs=False)
    try:
        db.connect()
        db.create_tables(CORE_MODELS)
        yield db
    finally:
        db.close()


@pytest.fixture()
def filesystem():
    dummy_bytes = bytes("DUMMY CONTENT", "UTF-8")
    mem_fs = MemoryFS()
    try:
        dir_light = "test/2021-12-25/Crab Nebula/Light/"
        dir_light_bad = dir_light + "/BAD/"
        dir_flats = "test/2021-12-25/Crab Nebula/Flats/"
        dir_darks = "test/2021-12-26/Darks/"

        mem_fs.makedirs(dir_light_bad)
        mem_fs.makedirs(dir_flats)
        mem_fs.makedirs(dir_darks)
        mem_fs.appendbytes("image01.fits", dummy_bytes)
        mem_fs.appendbytes(dir_light + "image02.fits", dummy_bytes)
        mem_fs.appendbytes(dir_light_bad + "image03.fits", dummy_bytes)
        mem_fs.appendbytes(dir_light + "image04.fits", dummy_bytes)
        mem_fs.appendbytes(dir_flats + "image05.fits", dummy_bytes)
        mem_fs.appendbytes(dir_darks + "image06.fits", dummy_bytes)
        mem_fs.appendbytes(dir_light + "BAD_image07.fits", dummy_bytes)
        mem_fs.appendbytes(dir_darks + "image08.fits.xz", dummy_bytes)
        mem_fs.appendbytes(dir_darks + "statistics.csv", dummy_bytes)

        yield mem_fs
    finally:
        mem_fs.close()
