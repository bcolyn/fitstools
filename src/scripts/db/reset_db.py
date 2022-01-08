#!/usr/bin/env python3
import os

import logzero
from logzero import logger

from fitstools.db.database_peewee import Root
from fitstools.db.scanner import DataStorage


def main():
    logzero.loglevel(logzero.INFO)

    database = "test.db"
    logger.info("trunacting database")
    os.remove(database)
    data_storage = DataStorage()
    data_storage.open(database)

    try:
        data_storage.begin_tx()
        Root.create(last_path=r"D:\Dropbox\Astro\Deep Sky\RAW", name="dropbox")
        Root.create(last_path=r"Z:\Deep Sky\Raw", name="archive")
        data_storage.commit_tx()
    except:
        data_storage.rollback()
    finally:
        data_storage.close()

    logger.info("done")


if __name__ == "__main__":
    main()
