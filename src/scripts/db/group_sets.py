#!/usr/bin/env python3
import traceback

import logzero
from logzero import logger

from fitstools.analysis.setbuilder import SetBuilder
from fitstools.db.scanner import DataStorage


def main(database="prod.db"):
    logzero.loglevel(logzero.INFO)

    data_storage = DataStorage()
    data_storage.open(database)

    logger.info("combining images into image sets.")
    try:
        data_storage.begin_tx()
        (img_count, set_count) = SetBuilder.combine()
        logger.info("Grouped %d images in %d sets" % (img_count, set_count))
        data_storage.commit_tx()
    except Exception as err:
        logger.error(err)
        traceback.print_exc()
        data_storage.rollback()
    finally:
        data_storage.close()

    logger.info("done")


if __name__ == "__main__":
    main()
