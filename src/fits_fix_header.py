#!/usr/bin/env python3
import os
from pathlib import Path

from astropy.io import fits
from astropy.io.fits import HDUList

from fitstools.util import is_fits


def main():
    """ Main entry point of the app """
    dir = 'D:\\Dropbox\\Astro\\Deep Sky\\RAW\\ZWO_ASI183MM\\2020-05-30\\Light\\MISNAMED'
    out = 'D:\\Dropbox\\Astro\\Deep Sky\\RAW\\ZWO_ASI183MM\\2020-05-30\\Light\\MISNAMED\\fix'
    header = "OBJECT"
    value = "M57"
    main_args(dir, out, header, value)


def list_dir(dir):
    return os.scandir(dir)


def fix_file(file: os.DirEntry, output, header, value):
    hdul: HDUList
    with fits.open(file.path, mode='readonly') as hdul:
        outputfile = Path(output, file.name)
        for hdu in hdul:
            data = hdu.data
            headers = hdu.header
            headers[header] = value
            fits.append(outputfile, data, headers)


def main_args(dir, output, header, value):
    files = list_dir(dir)
    for file in files:
        if is_fits(file):
            fix_file(file, output, header, value)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
