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
    logger.info("reading headers of file %s", file.full_filename())
    file_format = FileFormatManager.get_format(file)
    (images, meta) = file_format.import_file(file)
    assert len(meta) > 0
    logger.info("%d images with %d header fields" % (len(images), len(meta)))
    return images, meta


def main():
    logzero.loglevel(logzero.INFO)

    database = "test_min.db"

    data_storage = DataStorage()
    data_storage.open(database)

    logger.info("analyzing files for metadata")

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
    logger.info("done")


def main_serial():
    logzero.loglevel(logzero.INFO)

    database = "test_min.db"

    data_storage = DataStorage()
    data_storage.open(database)

    logger.info("analyzing files for metadata")

    try:
        query = File.select(File, Root).join(Root) \
            .where(File.rowid.not_in(Image.select(Image.file)))
        data_storage.begin_tx()
        try:
            for file in query:
                (images, metadata) = analyze(file)
                for image in images:
                    image.save()
                ImageMeta.bulk_create(metadata, 60)
            data_storage.commit_tx()
        except Exception:
            traceback.print_exc()
            data_storage.rollback()
    finally:
        data_storage.close()
    logger.info("done")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main_serial()
