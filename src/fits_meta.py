#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Benny Colyn"
__version__ = "0.1.0"
__license__ = "GPLv3"

import argparse
import csv
from os import DirEntry
from pathlib import Path
from typing import Dict, List, Sequence

from astropy.io.fits import Header, Card, VerifyError
from logzero import logger

from fitstools.util import read_headers, gather_files, is_fits, sha1sum, marked_bad


def main(args):
    roots = ["D:\\Dropbox\\Astro\\Deep Sky\\RAW", "E:\\Astro_Archief\\Deep Sky\\ZWO_ASI294MC_Pro"]
    for root in roots:
        gather_files(process_files, root,
                     file_filter=lambda x: is_fits(x) and not marked_bad(x),
                     dir_filter=lambda x: not marked_bad(x))


def process_files(files: Sequence[DirEntry]):
    try:
        process_files_throwing(files)
    except Exception as err:
        logger.exception(err)


def output_file(parent):
    return Path(parent, "headers.csv")


def write_csv(data: List[Dict], dir):
    field_names = []
    field_names_set = set()

    if not len(data):
        return

    for row in data:
        for key in row.keys():
            if key not in field_names_set:
                field_names.append(key)
                field_names_set.add(key)

    with open(output_file(dir), 'wt', newline='') as fh:
        writer = csv.DictWriter(fh, field_names, dialect='unix')
        writer.writeheader()
        writer.writerows(data)


def safe_dict(headers: Header) -> Dict[str, str]:
    result = {}
    for key in headers.keys():
        card: Card = headers.cards[key]
        try:
            result[key] = card.value
        except VerifyError as ve:
            if key == "OBJECT":
                card._image = card._image.replace('\t', ' ')  # tabs, even if non-printable, are common in my FITS files
                result[key] = card.value
            else:
                raise ve
    return result


def process_files_throwing(files: Sequence[DirEntry]):
    parent = Path(files[0].path).parent
    logger.info("Folder: " + str(parent))
    if output_file(parent).exists():
        return
    data = []
    file: DirEntry
    for file in files:
        logger.info(file.path)
        headers = safe_dict(read_headers(file.path))
        sanity_check(headers, file)
        row = {"FILENAME": file.name, "FILESHA1": sha1sum(file)}
        row.update(headers)
        data.append(row)
    write_csv(data, parent)


def is_light_sub(headers):
    return "IMAGETYP" in headers.keys() and "light" in headers["IMAGETYP"].lower()


def needs_plate_solve(headers):
    return not has_coordinates(headers)


def has_coordinates(headers):
    return "OBJCTRA" in headers or "RA" in headers


def run_astap(path):
    raise Exception("not implemented")


def sanity_check(headers: Dict[str, str], file: DirEntry):
    if is_light_sub(headers):
        if needs_plate_solve(headers):
            run_astap(file.path)


def get_args():
    parser = argparse.ArgumentParser()
    # Required positional argument
    # parser.add_argument("arg", help="Required positional argument")
    # Optional argument flag which defaults to False
    parser.add_argument("-f", "--flag", action="store_true", default=False)
    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-n", "--name", action="store", dest="name")
    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")
    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))
    return parser.parse_args()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    args = get_args()
    main(args)
