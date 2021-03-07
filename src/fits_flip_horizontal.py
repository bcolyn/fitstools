#!/usr/bin/env python3
import argparse
import os
from glob import glob
from pathlib import Path

from astropy.io import fits

dirs = [
    (r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2020-11-06", r"C:\TEMP\flipping2\2020-11-06"),
    (r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2021-02-10", r"C:\TEMP\flipping2\2021-02-10"),
    (r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2021-02-26", r"C:\TEMP\flipping2\2021-02-26")
]


def main():
    for (dir_in, dir_out) in dirs:
        files = glob(os.path.join(dir_in, "**/*.fit"))
        for file in files:
            file_out = file.replace(dir_in, dir_out)
            out_dir = Path(file_out).parent
            out_dir.mkdir(exist_ok=True, parents=True)
            print(file)
            flip_file(file, file_out)


def main1():
    parser = argparse.ArgumentParser(description='Flip back subs that have become flipped due to Sharpcap')
    parser.add_argument('inputfile')
    parser.add_argument('outputdir')
    args = parser.parse_args()
    inputfile = args.inputfile
    filename = Path(inputfile).name
    outputfile = os.path.join(args.outputdir, filename)

    print("input = %s, output = %s" % (inputfile, outputfile))

    flip_file(inputfile, outputfile)


def flip_file(inputfile, outputfile):
    with fits.open(inputfile) as hdul:
        hdul[0].header["FLIPPED"] = True
        hdul[0].data = hdul[0].data[:, :: -1]
        hdul.writeto(outputfile, overwrite=True)


if __name__ == "__main__":
    main()
