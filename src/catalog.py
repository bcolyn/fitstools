import csv
from typing import *
from typing import List, Any

import astropy.io.fits as fits
import astropy.wcs as wcs
import numpy as np
import astropy.units as u
import os

from logzero import logger

from astropy.coordinates import SkyCoord
from astropy.io.fits import Header


class Entry:
    def __init__(self, c: SkyCoord, name: str):
        self.coord = c
        self.name = name

    @classmethod
    def from_ra_dec(ra, dec, name):
        coord = SkyCoord(ra=ra * u.hour, dec=dec * u.deg)
        return Entry(coord, name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class Catalogs:
    _catalog: List[Entry]

    def __init__(self) -> None:
        super().__init__()
        self._catalog = []
        self.load_data()

    def add_to_catalog(self, entry):
        self._catalog.append(entry)

    def load_csv(self, file):
        with open(file, newline='', encoding="utf-8") as fh:
            fh.readline()  # skip first line
            fh.readline()  # skip 2nd line
            reader = csv.reader(fh)
            for line in reader:
                if len(line) < 3:
                    continue
                ra_deg = (float(line[0]) / (864000 / 360)) * u.deg
                dec_deg = (float(line[1]) / (324000 / 90)) * u.deg
                coord = SkyCoord(ra_deg, dec_deg)
                self.add_to_catalog(Entry(coord, line[2]))

    def load_data(self):
        our_path = os.path.dirname(__file__)
        deep_sky_file = os.path.join(our_path, "../data/deep_sky.csv")
        hyperleda_file = os.path.join(our_path, "../data/hyperleda.csv")
        logger.info("loading deep sky catalog")
        self.load_csv(deep_sky_file)
        logger.info("loading hyperleda catalog")
        self.load_csv(hyperleda_file)
        logger.info("done loading catalogs")

    def find_objects(self, header: Header):
        tmp = wcs.WCS(header)
        print(tmp.calc_footprint())
        result = []
        logger.info("searching catalog")
        for obj in self._catalog:
            res = tmp.footprint_contains(obj.coord)
            if res:
                result.append(obj)
        logger.info("returning " + str(result))
        return result

    # def find_objects(self, header: Header):
    #   tmp = wcs.WCS(header)
    #   wcs.
    #   https: // docs.astropy.org / en / stable / coordinates / matchsep.html  # searching-around-coordinates
    # tmp = wcs.WCS(header)
    # return tmp.all_world2pix(self.catalog, 0)
    # return tmp.all_world2pix([1,2,3], [1,1,1], 1, ra_dec_order=True)
