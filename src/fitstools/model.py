from datetime import datetime, date
from enum import Enum, auto


class ImageType(Enum):
    UNKNOWN = auto()
    BIAS = auto()
    DARK = auto()
    FLAT = auto()
    LIGHT = auto()
    BADPIXELMAP = auto()
    MASTER_FLAT = auto()
    MASTER_DARK = auto()
    MASTER_DARKFLAT = auto()
    MASTER_BIAS = auto()
    INTEGRATION = auto()


class ImageMeta:
    img_type: ImageType = ImageType.UNKNOWN
    exposure: float = None
    camera_temperature: float = None
    camera_name: str = None
    object_name: str = None
    filter: str = None
    xbin: int = None
    ybin: int = None
    gain: int = None
    offset: int = None
    telescope: str = None
    datetime_local: datetime = None
    datetime_utc: datetime = None


class ImageSetMeta:
    img_type: ImageType = ImageType.UNKNOWN
    exposure: float = None
    camera_temperature: float = None
    camera_name: str = None
    object_name: str = None
    filter: str = None
    xbin: int = None
    ybin: int = None
    gain: int = None
    offset: int = None
    telescope: str = None
    session_date: date = None
