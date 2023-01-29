from enum import Enum, auto


class File:
    pass


class Image:
    pass


class FrameType(Enum):
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


class ImageSetMeta:
    img_type: FrameType = FrameType.UNKNOWN
    exposure: float = None
    temp: float = None
    object_name: str = None
    camera: str = None
    filter: str = None
    xbin: int = None
    ybin: int = None
    gain: int = None
    offset: int = None
    telescope: str = None


class ImageSet:
    pass
