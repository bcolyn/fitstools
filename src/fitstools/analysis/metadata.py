from pathlib import Path

from abc import ABC, abstractmethod
from typing import Dict, List

from astropy.io.fits import Header, VerifyError
from logzero import logger

from fitstools.model import ImageSetMeta, FrameType


class MetadataAnalyser:

    @classmethod
    def normalize(cls, metadata: Dict[str, str], file: Path) -> ImageSetMeta:
        support = Support.find(metadata, file)
        return support.normalize(metadata)


class Support(ABC):
    DEFAULT_PRIO = 1000
    fits_image_type: str
    fits_image_type_map: Dict[str, FrameType]
    _support_types: List["Support"] = []

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        Support._support_types.append(cls())
        Support._support_types.sort(key=lambda f: f._prio(), reverse=True)

    @classmethod
    def find(cls, headers, path) -> "Support":
        for support in cls._support_types:
            if support._accept(headers, path):
                return support

    @abstractmethod
    def normalize(self, metadata) -> ImageSetMeta:
        pass

    @abstractmethod
    def _accept(self, headers, path) -> bool:
        pass

    def _prio(self) -> int:
        return Support.DEFAULT_PRIO

    @staticmethod
    def _match_in_header(headers, key, substring):
        return key in headers and headers[key].find(substring) >= 0


class _DefaultMapping:
    _fits_image_type_header = "IMAGETYP"
    _fits_image_type_map = {
        "LIGHT": FrameType.LIGHT,
        "DARK": FrameType.DARK,
        "FLAT": FrameType.FLAT,
        "BIAS": FrameType.BIAS,
        "Light Frame": FrameType.LIGHT,
        "Dark Frame": FrameType.DARK,
        "Flat Frame": FrameType.FLAT,
        "Bias Frame": FrameType.BIAS
    }

    @staticmethod
    def _map_meta(header, key, value_map, missing_value):
        if key in header:
            header_value = header[key]
            if header_value in value_map:
                return value_map[header_value]
        return missing_value

    def _std_mapping(self, metadata) -> ImageSetMeta:
        meta = ImageSetMeta()
        meta.img_type = self._map_meta(metadata, self._fits_image_type_header, self._fits_image_type_map,
                                       FrameType.UNKNOWN)
        meta.camera = _header(metadata, "INSTRUME")
        meta.exposure = _float(_header(metadata, "EXPOSURE", "EXPTIME"))
        meta.temp = _float(_header(metadata, "CCD-TEMP", "SET-TEMP"))
        meta.object_name = _header(metadata, "OBJECT")
        meta.filter = _header(metadata, "FILTER")
        meta.xbin = _int(_header(metadata, "XBINNING"))
        meta.ybin = _int(_header(metadata, "YBINNING"))
        meta.gain = _int(_header(metadata, "GAIN"))
        meta.offset = _int(_header(metadata, "OFFSET"))
        meta.telescope = _header(metadata, "TELESCOP")
        return meta


class GenericSupport(Support, _DefaultMapping):

    def normalize(self, metadata) -> ImageSetMeta:
        return self._std_mapping(metadata)

    def _accept(self, headers, path) -> bool:
        logger.info("Cannot determine creator software of FITS file %s, falling back to generic support." % path)
        return True

    def _prio(self) -> int:
        return 0


class SGPSupport(Support, _DefaultMapping):

    def normalize(self, metadata):
        return self._std_mapping(metadata)

    def _accept(self, headers, path):
        return self._match_in_header(headers, "CREATOR", "Sequence Generator Pro")


class APTSupport(Support, _DefaultMapping):

    def normalize(self, metadata):
        return self._std_mapping(metadata)

    def _accept(self, headers, path):
        return self._match_in_header(headers, "SWCREATE", "Astro Photography Tool")


class NinaSupport(Support, _DefaultMapping):

    def normalize(self, metadata):
        return self._std_mapping(metadata)

    def _accept(self, headers, path):
        return self._match_in_header(headers, "SWCREATE", "N.I.N.A.")


def _option(function):
    def wrapper(*args, **kwargs):
        if len(args) > 0 and args[0] is not None:
            return function(*args, **kwargs)

    return wrapper


_int = _option(int)
_float = _option(float)


def _find_header_card(headers: Header, *fieldnames):
    for fieldname in fieldnames:
        if fieldname in headers:
            return headers.cards[fieldname]
    return None


def _header(headers: Header, *fieldnames):
    card = _find_header_card(headers, *fieldnames)
    if card is None:
        return None
    try:
        return card.value
    except VerifyError:
        card._image = card._image.replace('\t', ' ')  # tabs, even if non-printable, are common in my FITS files
        return card.value
