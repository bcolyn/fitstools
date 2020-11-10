#!/usr/bin/env python3
"""
Module Docstring
"""
from pathlib import Path

from astropy.io import fits
from astropy.units import Quantity
from logzero import logger
from astropy.stats import SigmaClip

__author__ = "Your Name"
__version__ = "0.1.0"
__license__ = "MIT"

from astropy.stats import sigma_clipped_stats, gaussian_sigma_to_fwhm

from photutils import *

max_workers = int(os.cpu_count() * 0.8)


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
    import numpy as np
    with fits.open(filename) as hdul:
        data = hdul[0].data
    log_info("file   = ", filename)
    log_info("type   = ", hdul[0].header["IMAGETYP"])
    log_info("gain   = ", hdul[0].header["GAIN"])
    log_info("offset = ", hdul[0].header["OFFSET"])
    log_info("min    = ", np.min(data))
    log_info("max    = ", np.max(data))
    log_info("basic stats")
    mean, median, std = sigma_clipped_stats(data, sigma=3.0, cenfunc=np.mean, stdfunc=np.std)
    log_info("median = ", median)
    log_info("avg    = ", mean)
    log_info("subtracting background")
    subtracted = data - median
    background = np.zeros(data.shape) + median
    log_info("finding detection threshold")
    threshold = median + 5 * std
    log_info("detecting sources")
    sources = detect_sources(subtracted, threshold, 8)
    log_info("sources found: ", sources.nlabels)
    log_info("measuring sources")
    props = source_properties(subtracted, sources, background=background)
    table = props.to_table(['eccentricity', 'semimajor_axis_sigma', 'semiminor_axis_sigma'])
    med_ecc = np.median(table['eccentricity'])
    log_info("ecc    = ", med_ecc)
    fwhm_hi = table['semimajor_axis_sigma']
    fwhm_lo = table['semiminor_axis_sigma']
    med_fwhm: Quantity = np.median(fwhm_hi) * gaussian_sigma_to_fwhm  # + numpy.median(fwhm_lo)) / 2.0
    min_fwhm: Quantity = np.median(fwhm_lo) * gaussian_sigma_to_fwhm
    log_info("fwhm   = ", med_fwhm)

    return [filename.name, median, sources.nlabels, med_fwhm.value, med_ecc, min_fwhm.value]


def image_stats_mp(filename: Path):
    import logging
    import logzero
    logzero.loglevel(logging.WARNING)
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        return image_stats(filename)


class FastBackground2D(Background2D):
    def _calc_coordinates(self):
        pass


def log_info(*args):
    args = map(str, args)
    logger.info("".join(args))


def main1():
    filename = r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2020-01-15\Light\IC 405_2020-01-15T193701_60sec_OIII__-15C_frame8.fit"
    import numpy
    with fits.open(filename) as hdul:
        data = hdul[0].data
    sigma_clip = SigmaClip(sigma=3., maxiters=5)
    bkg_estimator = MeanBackground()
    bkg = FastBackground2D(data, (128, 128), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    subtracted = data - bkg.background
    print("median subtracted value " + str(numpy.median(subtracted)))


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


def main3():
    images = list_images()
    from concurrent.futures.thread import ThreadPoolExecutor
    from concurrent.futures.process import ProcessPoolExecutor
    # executor = ThreadPoolExecutor(max_workers=max_workers)
    executor = ProcessPoolExecutor(max_workers=max_workers)
    results = executor.map(image_stats_mp, images)
    executor.shutdown()
    print(list(results))


def main4():
    images = list_images()
    import multiprocessing as mp
    with mp.Pool() as pool:
        results = pool.map(image_stats_mp, images)
    print(list(results))


def list_images():
    image_dir = r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2020-01-15\Light"
    images = []
    for f in os.scandir(image_dir):
        image = Path(f)
        if image.name.startswith("IC 405"):
            images.append(image.resolve())
    return images


def main():
    fits_image_filename = [
        #        r"D:\Dropbox\Astro\Calibration\ASI183MM Pro\Bias\gain111_-15\raw\Bias_2019-06-04T031420_0sec_None__-15C_frame12.fit",
        #        r"E:\Astro_Archief\Calibration\ASI183MM Pro\2020-04-27\Dark\D183MM_2020-04-28T023615_60sec_None__-15C_frame218.fit",
        r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2020-01-15\Light\IC 405_2020-01-15T193701_60sec_OIII__-15C_frame8.fit"
    ]
    for file in fits_image_filename:
        image_stats(Path(file))


if __name__ == "__main__":
    # numpy.__config__.show()
    """ This is executed when run from the command line """
    import time

    start = time.time()
    main4()
    end = time.time()
    print(end - start)
    print("max workers = " + str(max_workers))

    # import cProfile
    #
    # start = time.time()
    # cProfile.run("main1()", "bgstats")
    # end = time.time()
    # print("time used: " + str(end - start))
    #
    # import pstats
    #
    # p = pstats.Stats('bgstats')
    # p.sort_stats('cumtime').print_stats()
