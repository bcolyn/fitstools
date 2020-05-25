from enum import Enum, unique, auto
from typing import Dict


class FrameType(Enum):
    BIAS = auto()
    DARK = auto()
    FLAT = auto()
    LIGHT = auto()


class Support(object):
    fits_image_type: str
    fits_image_type_map: Dict[str, FrameType]

    def image_type(self, headers) -> FrameType:
        return self.fits_image_type_map[headers[self.fits_image_type]]

    def check_sanity(self, headers):
        if self.fits_image_type not in headers:
            raise RuntimeError("missing required header:" + self.fits_image_type)
        if self.image_type(headers) == FrameType.LIGHT and self.needs_plate_solve(headers):
            raise RuntimeError("no plate solving implemented")

    @staticmethod
    def needs_plate_solve(headers: Dict):
        return "OBJCTRA" not in headers.keys()


class SGPSupport(Support):
    fits_image_type = "IMAGETYP"
    fits_image_type_map = {
        "LIGHT": FrameType.LIGHT,
        "DARK": FrameType.DARK,
        "FLAT": FrameType.FLAT,
        "BIAS": FrameType.BIAS
    }


class APTSupport(Support):
    fits_image_type = "IMAGETYP"
    fits_image_type_map = {
        "Light Frame": FrameType.LIGHT,
        "Dark Frame": FrameType.DARK,
        "Flat Frame": FrameType.FLAT,
        "Bias Frame": FrameType.BIAS
    }


@unique
class Creator(Enum):
    SequenceGeneratorPro = {"creator_header": "CREATOR", "creator_check": "Sequence Generator Pro",
                            "support": SGPSupport()}
    AstroPhotographyTool = {"creator_header": "SWCREATE", "creator_check": "Astro Photography Tool",
                            "support": APTSupport()}

    def creator_header(self):
        return self.value["creator_header"]

    def creator_check(self):
        return self.value["creator_check"]

    def support(self) -> Support:
        return self.value["support"]

    @classmethod
    def find_creator(cls, headers: Dict):
        for creator in list(Creator):
            if creator.creator_header() in headers and \
                    headers[creator.creator_header()].find(creator.creator_check()) >= 0:
                return creator
        raise RuntimeError("unsupported software created this file ", headers)
