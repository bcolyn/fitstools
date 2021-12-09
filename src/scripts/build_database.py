#!/usr/bin/env python3

from fitstools.db.database_peewee import Root
from fitstools.db.scanner import DataStorage, Importer


def main():
    import logging
    logger = logging.getLogger('peewee')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    root_path = r"Z:\Deep Sky\Raw\ZWO_ASI183MC\2019-11-20"
    database = ":memory:"

    data_storage = DataStorage()
    data_storage.open(database)
    Root.create(last_path=root_path, name="test_root")
    try:
        importer = Importer(data_storage)
        importer.import_files()
    finally:
        data_storage.close()


if __name__ == "__main__":
    main()
