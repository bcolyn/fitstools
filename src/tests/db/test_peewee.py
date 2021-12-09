import logging

import pytest
from playhouse.reflection import print_table_sql

from fitstools.db.database_peewee import *

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

MODELS = [Root, File]


@pytest.fixture
def database():
    db = SqliteDatabase(':memory:', pragmas={
        'journal_mode': 'wal',
        'cache_size': -1 * 64000,  # 64MB
        'foreign_keys': 1
    })
    db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables(MODELS)
    yield db
    db.close()


def test_print_sql(database):
    print_table_sql(Root)


def test_create_root(database):
    root = Root()
    root.name = "dummy"
    root.last_path = r'C:\TEMP'
    root.save()
