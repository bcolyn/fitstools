import csv
import os

import numpy as np
import pandas
import pytest
from astropy import units as u
from astropy import wcs
from astropy.coordinates import ICRS
from astropy.io import fits
from astropy_healpix import HEALPix
from logzero import logger

from src.fitstools.catalog import Catalogs
from src.fitstools.util import read_headers

our_path = os.path.dirname(__file__)
deep_sky_file = os.path.join(our_path, "../fitstools/data/deep_sky.csv")
hyperleda_file = os.path.join(our_path, "../fitstools/data/hyperleda.csv")


def test_csv_reader():
    logger.info("start")
    count = 0
    catalog = []
    with open(hyperleda_file, newline='', encoding="utf-8") as fh:
        fh.readline()  # skip first line
        fh.readline()  # skip 2nd line
        reader = csv.reader(fh)
        for line in reader:
            if len(line) < 3:
                continue
            ra_deg = (int(line[0]) / float(864000 / 360))  # * u.deg
            dec_deg = (int(line[1]) / float(324000 / 90))  # * u.deg
            # catalog.append([ra_deg, dec_deg])
            count += 1

    logger.info("stop - " + str(count))


def test_pandas_reader():
    dir = "C:\\TEMP\\"
    file = dir + "M57_2020-05-30T025615_30sec_HaOIII_COLD_-20C_frame78.fit"
    header = read_headers(file)
    w = wcs.WCS(header).celestial
    hp = HEALPix(nside=16, frame='icrs')

    logger.info("start")
    df = pandas.read_csv(hyperleda_file, skiprows=1, engine='c', usecols=[0, 1, 2], header=0,
                         names=['ra', 'dec', 'name'], dtype={'ra': np.int, 'dec': np.int, 'name': np.object})
    df['ra'] = df['ra'] / np.float(864000 / 360)
    df['dec'] = df['dec'] / np.float(324000 / 90)
    ra = df.ra.to_numpy() * u.deg
    dec = df.dec.to_numpy() * u.deg
    df['hp'] = hp.lonlat_to_healpix(ra, dec)

    logger.info("stop - " + str(len(df)))
    cat = df.groupby('hp')
    logger.info("groupby - " + str(len(df)))

@pytest.fixture()
def catalog():
    catalog = Catalogs()
    return catalog


def test_find_objects(catalog):
    dir = "C:\\TEMP\\"
    file = dir + "M57_2020-05-30T025615_30sec_HaOIII_COLD_-20C_frame78.fit"
    header = read_headers(file)
    objects = catalog.find_objects(header)
    logger.info(objects)
    # assert "M57/NGC6720/Ring_Nebula" in objects


def test_wcs_astap():
    # dir = "D:\\Dropbox\\Astro\\Deep Sky\\RAW\\ZWO_ASI294MC\\2020-05-29\\Light\\"
    dir = "C:\\TEMP\\"
    file = dir + "M57_2020-05-30T025615_30sec_HaOIII_COLD_-20C_frame78.fit"
    with fits.open(file, mode='readonly') as hdul:
        validation = wcs.validate(hdul)
        print(validation)
    print("------------------------------------------")

    header = read_headers(file)
    w = wcs.WCS(header).celestial
    print(w.wcs.name)
    w.wcs.print_contents()
    print("------------------------------------------")

    w.printwcs()
    print("------------------------------------------")

    fp = w.calc_footprint()
    for point in fp:
        c = ICRS(point[0] * u.degree, point[1] * u.degree)
        rahmsstr = c.ra.to_string(u.hour)
        decdmsstr = c.dec.to_string(u.degree, alwayssign=True)
        print(rahmsstr + ' ' + decdmsstr)


def test_wcs_sgp():
    dir = "D:\\Dropbox\\Astro\\Deep Sky\\RAW\\ZWO_ASI294MC\\2020-05-29\\Light\\"
    # dir = "C:\\TEMP\\"
    file = dir + "M57_2020-05-30T025615_30sec_HaOIII_COLD_-20C_frame78.fit"
    with fits.open(file, mode='readonly') as hdul:
        validation = wcs.validate(hdul)
        print(validation)
    print("------------------------------------------")

    header = read_headers(file)
    w = wcs.WCS(header).celestial
    print(w.wcs.name)
    w.wcs.print_contents()
    print("------------------------------------------")

    w.printwcs()
    print("------------------------------------------")

    fp = w.calc_footprint()
    for point in fp:
        c = ICRS(point[0] * u.degree, point[1] * u.degree)
        rahmsstr = c.ra.to_string(u.hour)
        decdmsstr = c.dec.to_string(u.degree, alwayssign=True)
        print(rahmsstr + ' ' + decdmsstr)


def test_sample():
    from matplotlib import pyplot as plt
    from astropy.io import fits
    from astropy.wcs import WCS

    # filename = get_pkg_data_filename('tutorials/FITS-images/HorseHead.fits')
    dir = "C:\\TEMP\\"
    filename = dir + "M57_2020_05_30T025615_30sec_HaOIII_COLD_20C_frame78_RGB_VNG_L.fit"

    hdu = fits.open(filename)[0]
    wcs = WCS(hdu.header).celestial

    fig = plt.figure()
    fig.add_subplot(111, projection=wcs)
    plt.imshow(hdu.data, origin='lower', cmap=plt.cm.viridis)
    plt.xlabel('RA')
    plt.ylabel('Dec')
    plt.show()

    # header = {
    #     'SIMPLE': 'T',
    #     'BITPIX': 16,
    #     'NAXIS': 2,
    #     'NAXIS1': 4144,
    #     'NAXIS2': 2822,
    #     'BZERO': 32768,
    #     'BSCALE': 1,
    #     'CRPIX1': 2072,
    #     'CRPIX2': 1411,
    #     'CTYPE1': 'RA---TAN',
    #     'CTYPE2': 'DEC--TAN',
    #     'OBJECT': 'M57     ',
    #     'DATE-LOC': '2020-05-30T02:10:15.8600892',
    #     'DATE-OBS': '2020-05-30T00:10:15.8600892',
    #     'IMAGETYP': 'LIGHT   ',
    #     'CREATOR': 'Sequence Generator Pro v3.1.0.479',
    #     'INSTRUME': 'ZWO ASI294MC Pro',
    #     'OBSERVER': 'Benny   ',
    #     'SITENAME': 'Ghent   ',
    #     'SITEELEV': 10,
    #     'SITELAT': '51 3 0.000',
    #     'SITELONG': '3 43 0.000',
    #     'FOCUSER': 'ASCOM Driver for SestoSenso',
    #     'FOCPOS': 827840,
    #     'FOCTEMP': 14.1513333333333,
    #     'FWHEEL': 'Manual Filter Wheel',
    #     'FILTER': 'HaOIII  ',
    #     'EXPOSURE': 30,
    #     'CCD-TEMP': 15.1,
    #     'SET-TEMP': 15,
    #     'XBINNING': 1,
    #     'CCDXBIN': 1,
    #     'YBINNING': 1,
    #     'CCDYBIN': 1,
    #     'RA': 283.397514641845,
    #     'DEC': 33.031484375,
    #     'CRVAL1': 283.397514641845,
    #     'CRVAL2': 33.031484375,
    #     'OBJCTRA': '18 53 35.404',
    #     'OBJCTDEC': '+33 01 53.344',
    #     'AIRMASS': 1.13055397853138,
    #     'OBJCTALT': 62.2290956850568,
    #     'CENTALT': 62.2290956850568,
    #     'FOCALLEN': 1480,
    #     'FLIPPED': 'F',
    #     'ANGLE': 258.37,
    #     'SCALE': 0.65415,
    #     'PIXSCALE': 0.65415,
    #     'POSANGLE': 258.369995117188,
    #     'GAIN': 120,
    #     'EGAIN': 3.99000000953674,
    #     'OFFSET': 30,
    # }
