#!/usr/bin/env python3

import logzero
from logzero import logger

from fitstools.db.scanner import DataStorage, Importer


def main(database="prod.db"):
    logzero.loglevel(logzero.INFO)

    data_storage = DataStorage()
    data_storage.open(database)

    try:
        data_storage.begin_tx()
        importer = Importer()
        for change_list in importer.import_files():
            logger.info("%d new files, %d changed files, %d deleted files", len(change_list.new_files),
                        len(change_list.changed_files), len(change_list.removed_files))
            logger.info("applying changes to database")
            change_list.apply_all()
            logger.info("done")
        data_storage.commit_tx()
    except:
        data_storage.rollback()
    finally:
        data_storage.close()


if __name__ == "__main__":
    main()
