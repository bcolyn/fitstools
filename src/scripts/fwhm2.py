import numpy as np
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from logzero import logger
from numpy import dtype
from photutils import *


def log_info(*args):
    args = map(str, args)
    logger.info("".join(args))

def main():
    filename = r"D:\Dropbox\Astro\Deep Sky\RAW\ZWO_ASI183MM\2020-11-06\Light\NGC 2366_2020-11-07T055054_120sec_Ha__-15C_frame6.fit"
    fast_bkg = False

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
    if fast_bkg:
        log_info("subtracting background (median)")
        data -= int(median)
        log_info("finding detection threshold")
        threshold = 5. * std
    else:
        log_info("caclulating background")
        bkground = Background2D(data, 50)
        log_info("subtracting background")
        data = data - bkground.background
        log_info("finding detection threshold")
        threshold = 5. * bkground.background_rms

    log_info("detecting sources")
    sources = detect_sources(data, threshold, 4)
    log_info("sources found: ", sources.nlabels)


    log_info("SourceCatalog:")
    catalog = SourceCatalog(data, sources)
    med_fwhm = np.median(catalog.fwhm)
    log_info("fwhm   = ", med_fwhm)
    med_ecc = np.median(catalog.eccentricity)
    log_info("ecc    = ", med_ecc)


if __name__ == "__main__":
    import cProfile
    cProfile.run("main()", "cprofile.stats")
