#!/usr/bin/env python3
import multiprocessing
import traceback

import logzero
from logzero import logger

from fitstools.analysis.fileformat import FileFormatManager
from fitstools.db.database_peewee import File, Image, Root, ImageMeta
from fitstools.db.scanner import DataStorage

PROCESSES = multiprocessing.cpu_count() - 1
CHUNKSIZE = 10


def analyze(file: File):
    logger.info("analyzing file %s", file.full_filename())
    file_format = FileFormatManager.get_format(file)
    result = file_format.import_file(file)
    return result


def main():
    logzero.loglevel(logzero.INFO)

    database = "test.db"

    data_storage = DataStorage()
    data_storage.open(database)

    try:
        with multiprocessing.Pool(processes=PROCESSES) as pool:
            query = File.select(File, Root).join(Root) \
                .where(File.rowid.not_in(Image.select(Image.file)))
            for (images, metadata) in pool.imap_unordered(analyze, query, CHUNKSIZE):
                try:
                    data_storage.begin_tx()
                    for image in images:
                        image.save()
                    ImageMeta.bulk_create(metadata, 20)
                    data_storage.commit_tx()
                except Exception:
                    traceback.print_exc()
                    data_storage.rollback()

    finally:
        data_storage.close()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
