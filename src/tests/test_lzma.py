import lzma
from pathlib import Path

from astropy.io import fits
from astropy.io.fits import HDUList


def test_read_lzma_header():
    filename = resolve_test_data('test_image.fits.xz')
    with lzma.open(filename) as f:
        hdul: HDUList = fits.open(f)
        hdul.info()
        print(repr(hdul[0].header))


def resolve_test_data(file):
    root = Path(__file__).parent
    path = Path(root, "test-data", file)
    assert path.exists()
    return path
