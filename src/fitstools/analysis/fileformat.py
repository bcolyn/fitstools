from astropy.io import fits
from astropy.io.fits import Header, Card, VerifyError

from fitstools.db.database_peewee import *


# fileformat plugins:
# check if a file can be accepted by extension and/or file magic
# read the file, extract number of images, image properties


class FileFormat:
    def accept(self, file: File):
        raise NotImplementedError()

    def import_file(self, file: File):
        raise NotImplementedError()


class FitsFileFormat(FileFormat):
    def import_file(self, file: File) -> [typing.List[Image], typing.List[Image]]:
        images = []
        metadata = []
        with file.fopen() as fd:
            with fits.open(fd) as hdul:
                primary = hdul[0]
                header = primary.header
                image = Image(file=file)
                header_dict = self.safe_dict(header)
                for (key, value) in header_dict.items():
                    meta = ImageMeta(image=image, key=key, value=value)
                    metadata.append(meta)
                images.append(image)
        return images, metadata

    def accept(self, file: File) -> bool:
        file_exts = file.get_file_exts()
        if len(file_exts):
            return file_exts[0] == "fit" or file_exts[0] == "fits"

    @staticmethod
    def safe_value(card: Card):
        try:
            return card.value
        except VerifyError as ve:
            if card.keyword == "OBJECT":
                card._image = card._image.replace('\t', ' ')  # tabs, even if non-printable, are common in my FITS files
                return card.value
            else:
                raise ve

    @staticmethod
    def safe_dict(headers: Header) -> typing.Dict[str, str]:
        result = {}
        card: Card
        for card in headers.cards:
            result[card.keyword] = FitsFileFormat.safe_value(card)
        return result


class FileFormatManager:
    FORMATS = [FitsFileFormat()]

    @staticmethod
    def get_format(file: File):
        for file_format in FileFormatManager.FORMATS:
            if file_format.accept(file):
                return file_format
