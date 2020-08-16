from astropy.io.fits import Header


class ImageMeta:
    x: int
    y: int
    channels: int

    def __init__(self, x: int, y: int, channels: int):
        self.x = x
        self.y = y
        self.channels = channels

    def center(self):
        return self.x / 2.0, self.y / 2.0

    @classmethod
    def from_fits(cls, header: Header):
        naxis = header["NAXIS"]
        x = header["NAXIS1"]
        y = header["NAXIS2"]
        channels = 1 if (naxis == 2) else header["NAXIS3"]
        return ImageMeta(x, y, channels)
