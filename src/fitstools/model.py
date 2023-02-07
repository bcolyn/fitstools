from datetime import datetime, date, timedelta
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


class NormalizedImageMeta:
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

    def session_date(self) -> date:
        """Calculates the session date. The session date is the date on which the night started during which these images
            were taken. This gives us one date to work with instead of 2 dates (before and after midnight).
        """

        # we prefer local date time, but not every piece of software gives us this
        # since we group images also by software, this isn't much of a problem (they all have it or none have it) but
        # it is more logical to use the local date time to determine night/day (esp for those far from UTC)
        # in the future we may be able to determine tz offset from GPS coords
        reference_date = self.datetime_local if self.datetime_local is not None else self.datetime_utc
        if reference_date is not None:
            if reference_date.hour < 12:  # before noon, morning hours, so we take the day before
                return reference_date.date() - timedelta(days=1)
            else:
                return reference_date.date()
