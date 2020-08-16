import os

import astropy.units as u
import astropy.wcs as wcs
import numpy as np
import pandas
from astropy.coordinates import SkyCoord
from astropy.io.fits import Header
from astropy.wcs.utils import pixel_to_skycoord
from astropy_healpix import HEALPix
from logzero import logger
from pandas.core.groupby import DataFrameGroupBy

from .image import ImageMeta


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
    _catalog: DataFrameGroupBy

    def __init__(self) -> None:
        super().__init__()
        self.hp = HEALPix(nside=16, frame='icrs')
        self._load_data()

    def find_objects(self, header: Header):
        logger.info("searching catalog")
        result = []
        world = wcs.WCS(header)
        footprint = world.calc_footprint().tolist()
        cx, cy = ImageMeta.from_fits(header).center()
        center_coord = pixel_to_skycoord(cx, cy, world, 1)
        corners = map(lambda t: SkyCoord(t[0], t[1], unit=world.world_axis_units), footprint)
        dist_corners = map(lambda x: center_coord.separation(x), corners)
        radius = max(dist_corners)
        hp_pix = self.hp.cone_search_skycoord(center_coord, radius=radius)
        for pix in hp_pix:
            group = self._catalog.get_group(pix)
            group_res = world.footprint_contains(SkyCoord(group.ra * u.deg, group.dec * u.deg))
            result.append(list(group[group_res].itertuples(index=False, name=None)))

        logger.info("returning " + str(result))
        return result

    def _load_csv(self, file):
        df = pandas.read_csv(file, skiprows=1, engine='c', usecols=[0, 1, 2], header=0,
                             names=['ra', 'dec', 'name'], dtype={'ra': np.int, 'dec': np.int, 'name': np.object})
        return df

    def _load_data(self):
        logger.info("loading catalogs")
        our_path = os.path.dirname(__file__)
        ds = self._load_deep_sky(our_path)
        leda = self._load_hyperleda(our_path)
        all = pandas.concat([ds, leda])
        all.ra = all.ra / np.float(864000 / 360)
        all.dec = all.dec / np.float(324000 / 90)
        ra = all.ra.to_numpy() * u.deg
        dec = all.dec.to_numpy() * u.deg
        all['hp'] = self.hp.lonlat_to_healpix(ra, dec)
        self._catalog = all.groupby('hp')
        logger.info("done loading catalogs")

    def _load_hyperleda(self, our_path):
        logger.info("loading hyperleda catalog")
        hyperleda_file = os.path.join(our_path, "../data/hyperleda.csv")
        return self._load_csv(hyperleda_file)

    def _load_deep_sky(self, our_path, ):
        logger.info("loading deep sky catalog")
        deep_sky_file = os.path.join(our_path, "../data/deep_sky.csv")
        return self._load_csv(deep_sky_file)
