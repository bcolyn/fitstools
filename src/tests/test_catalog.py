import csv
import os
from pathlib import Path

import numpy as np
import pandas
import pytest
from astropy import units as u
from astropy import wcs
from astropy.coordinates import ICRS
from astropy.io import fits
from astropy.io.fits import Header
from astropy_healpix import HEALPix
from logzero import logger
from . import sample_headers

from src.fitstools.catalog import Catalogs
from src.fitstools.util import read_headers

our_path = os.path.dirname(__file__)
deep_sky_file = os.path.join(our_path, "../fitstools/data/deep_sky.csv")
hyperleda_file = os.path.join(our_path, "../fitstools/data/hyperleda.csv")
test_file = os.path.join(Path(__file__).parent, "test-data\\M57_2020-05-30T022249_30sec_HaOIII_COLD_-17C_frame19.fit")

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
    header = read_headers(test_file)
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
    header = Header.fromstring(sample_headers.header_sgp_fixed_wcs, "\n")
    objects = catalog.find_objects(header)
    logger.info(objects)
    names = map(lambda t: t[2], objects)
    assert "M57/NGC6720/Ring_Nebula" in names
    assert "IC1296" in names


def test_wcs_astap():
    with fits.open(test_file, mode='readonly') as hdul:
        validation = wcs.validate(hdul)
        print(validation)
    print("------------------------------------------")

    header = read_headers(test_file)
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
    with fits.open(test_file, mode='readonly') as hdul:
        validation = wcs.validate(hdul)
        print(validation)
    print("------------------------------------------")

    header = read_headers(test_file)
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
