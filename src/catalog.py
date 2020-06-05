import csv
import os
from pathlib import Path
from typing import *

import astropy.units as u
import astropy.wcs as wcs
from astropy.coordinates import SkyCoord
from astropy.io.fits import Header
from astropy.wcs.utils import pixel_to_skycoord
from astropy_healpix import HEALPix
from logzero import logger

from src.image import ImageMeta


class Entry:
    def __init__(self, ra, dec, name: str):
        self.ra = ra
        self.dec = dec
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class Catalogs:
    _catalog: Dict[int, List[Entry]]

    def __init__(self) -> None:
        super().__init__()
        self._catalog = {}
        self.hp = HEALPix(nside=16, frame='icrs')
        self._cache_file = Path("~/fitstools.cache").expanduser()
        self._load_data()

    def find_objects(self, header: Header):
        world = wcs.WCS(header)
        result = []
        cx, cy = ImageMeta.from_fits(header).center()
        center_coord = pixel_to_skycoord(cx, cy, world, 1)
        footprint = world.calc_footprint().tolist()

        logger.info("searching catalog")
        corners = map(lambda t: SkyCoord(t[0], t[1], unit=world.world_axis_units), footprint)
        dist_corners = map(lambda x: center_coord.separation(x), corners)
        radius = max(dist_corners)
        hp_pix = self.hp.cone_search_skycoord(center_coord, radius=radius)
        keys = map(str, hp_pix)
        for pix in keys:
            if pix in self._catalog:
                for obj in self._catalog[pix]:
                    res = world.footprint_contains(SkyCoord(obj.ra, obj.dec))
                    if res:
                        result.append(obj)
        logger.info("returning " + str(result))
        return result

    def _cache_exists(self):
        return self._cache_file.exists()

    def _load_csv(self, file, catalog: Dict):
        with open(file, newline='', encoding="utf-8") as fh:
            fh.readline()  # skip first line
            fh.readline()  # skip 2nd line
            reader = csv.reader(fh)
            for line in reader:
                if len(line) < 3:
                    continue
                ra_deg = (float(line[0]) / (864000 / 360)) * u.deg
                dec_deg = (float(line[1]) / (324000 / 90)) * u.deg
                entry = Entry(ra_deg, dec_deg, line[2])
                pix = str(self.hp.lonlat_to_healpix(ra_deg, dec_deg))
                lst = catalog[pix] if pix in catalog else []
                lst.append(entry)
                catalog[pix] = lst

    def _load_data(self):
        logger.info("loading cache")
        #self._catalog = shelve.open(str(self._cache_file), writeback=True)
        self._catalog = {}
        if len(self._catalog.keys()) != 0:
            logger.info("done loading cache")
            return
        else:
            tmp = {}
            our_path = os.path.dirname(__file__)
            self._load_deep_sky(our_path, tmp)
            self._load_hyperleda(our_path, tmp)
            logger.info("done loading catalogs")
            logger.info("saving cache")
            self._catalog.update(tmp)
            #self._catalog.sync()
            logger.info("done saving cache")

    def _load_hyperleda(self, our_path, tmp):
        logger.info("loading hyperleda catalog")
        hyperleda_file = os.path.join(our_path, "../data/hyperleda.csv")
        self._load_csv(hyperleda_file, tmp)

    def _load_deep_sky(self, our_path, tmp):
        logger.info("loading deep sky catalog")
        deep_sky_file = os.path.join(our_path, "../data/deep_sky.csv")
        self._load_csv(deep_sky_file, tmp)

    def close(self):
        pass
        #self._catalog.close()
