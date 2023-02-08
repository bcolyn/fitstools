#!/usr/bin/env python3
import os
from pathlib import Path

import logzero
from logzero import logger

from fitstools.db.database_peewee import Root
from fitstools.db.scanner import DataStorage


def main(database="test_min.db", data_root=r"Z:\Deep Sky\Raw\ZWO_ASI294MM\2020-11-02"):
    logzero.loglevel(logzero.INFO)

    logger.info("truncating database")
    if Path(database).exists():
        os.remove(database)
    data_storage = DataStorage()
    data_storage.open(database)

    try:
        data_storage.begin_tx()
        # Root.create(last_path=r"D:\Dropbox\Astro\Deep Sky\RAW", name="dropbox")
        Root.create(last_path=data_root, name="archive")
        data_storage.commit_tx()
    except:
        data_storage.rollback()
    finally:
        data_storage.close()

    logger.info("done")


if __name__ == "__main__":
    main()
