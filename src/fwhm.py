#!/usr/bin/env python3
"""
Module Docstring
"""
from pathlib import Path

import numpy
from astropy.io import fits
from astropy.units import Quantity
from logzero import logger
from astropy.stats import SigmaClip

__author__ = "Your Name"
__version__ = "0.1.0"
__license__ = "MIT"

from astropy.stats import sigma_clipped_stats, gaussian_sigma_to_fwhm

from photutils import *


def image_stats2(filename: Path):
    with fits.open(filename) as hdul:
        data = hdul[0].data
    log_info("basic stats")
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)
    log_info("finding detection threshold")
    threshold = median + 5 * std
    # threshold = detect_threshold(data, 3)
    log_info("detecting peaks")
    peaks = find_peaks(data, threshold)
    log_info("peaks found: ", len(peaks))


def image_stats(filename: Path):
    with fits.open(filename) as hdul:
        data = hdul[0].data
    log_info("file   = ", filename)
    log_info("type   = ", hdul[0].header["IMAGETYP"])
    log_info("gain   = ", hdul[0].header["GAIN"])
    log_info("offset = ", hdul[0].header["OFFSET"])
    log_info("median = ", numpy.median(data))
    log_info("avg    = ", numpy.average(data))
    log_info("min    = ", numpy.min(data))
    log_info("max    = ", numpy.max(data))

    # peaks = find_peaks(data, threshold, npeaks=20, centroid_func=centroid_2dg)
    # print(peaks)
    log_info("basic stats")
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)
    # log_info("calculating background")
    # sigma_clip = SigmaClip(sigma=3.)
    # bkg_estimator = MedianBackground()  # SExtractorBackground()  #
    # bkg = Background2D(data, (50, 50), filter_size=(3, 3), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    # log_info("subtracting background")
    # subtracted = data - bkg.background
    subtracted = data
    log_info("finding detection threshold")
    # threshold = detect_threshold(subtracted, 3)
    threshold = median + 5 * std
    log_info("detecting sources")
    sources = detect_sources(subtracted, threshold, 8)
    log_info("sources found: ", sources.nlabels)
    log_info("measuring sources")
    table = source_properties(subtracted, sources)  # background=median
    # for row in table:
    #     print("ecc    = ", row.eccentricity)
    #     print("semi   = ",row.semimajor_axis_sigma)
    #     print("fwhm   = ", 2.355 * row.semimajor_axis_sigma)
    med_ecc = numpy.median(table.eccentricity)
    log_info("ecc    = ", med_ecc)

    fwhm_hi = table.semimajor_axis_sigma * gaussian_sigma_to_fwhm
    fwhm_lo = table.semiminor_axis_sigma * gaussian_sigma_to_fwhm
    med_fwhm: Quantity = numpy.median(fwhm_hi)  # + numpy.median(fwhm_lo)) / 2.0
    min_fwhm: Quantity = numpy.median(fwhm_lo)
    log_info("fwhm   = ", med_fwhm)

    # daofind = DAOStarFinder(fwhm=med_fwhm.value, threshold=5. * std)
    # sources = daofind(data - median)
    # print(sources)

    return [filename.name, median, sources.nlabels, med_fwhm.value, med_ecc, min_fwhm.value]


def log_info(*args):
    args = map(str, args)
    logger.info("".join(args))


def main3():
    filename = r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2020-01-15\Light\IC 405_2020-01-15T193701_60sec_OIII__-15C_frame8.fit"
    with fits.open(filename) as hdul:
        data = hdul[0].data
    sigma_clip = SigmaClip(sigma=3., maxiters=5)
    bkg_estimator = SExtractorBackground()  # MedianBackground()
    bkg = Background2D(data, (500, 500), filter_size=(30, 30), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    subtracted = data - bkg.background
    print(numpy.median(subtracted))


def main2():
    image_dir = r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2020-01-15\Light"
    data = []
    for f in os.scandir(image_dir):
        image = Path(f)
        if image.name.startswith("IC 405"):
            row = image_stats(image.resolve())
            data.append(row)
    import csv
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "median", "nlabels", "med_fwhm", "med_ecc"])
        writer.writerows(data)


def main():
    fits_image_filename = [
        #        r"D:\Dropbox\Astro\Calibration\ASI183MM Pro\Bias\gain111_-15\raw\Bias_2019-06-04T031420_0sec_None__-15C_frame12.fit",
        #        r"E:\Astro_Archief\Calibration\ASI183MM Pro\2020-04-27\Dark\D183MM_2020-04-28T023615_60sec_None__-15C_frame218.fit",
        r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2020-01-15\Light\IC 405_2020-01-15T193701_60sec_OIII__-15C_frame8.fit"
    ]
    for file in fits_image_filename:
        image_stats(Path(file))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main2()
    # import cProfile
    # cProfile.run("main3()", "bgstats")

    # import pstats
    # p = pstats.Stats('bgstats')
    # p.sort_stats('cumtime').print_stats()
