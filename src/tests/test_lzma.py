import lzma
from astropy.io import fits
from astropy.io.fits import HDUList


def test_read_lzma_header():
    filename = r'E:\Astro_Archief\Deep Sky\Raw\ZWO_ASI183MM_Pro\2019-03-29\Light\Medusa_2019-03-29T212651_120sec_SII__-25C_frame8.fit.xz'
    with lzma.open(filename) as f:
        hdul: HDUList = fits.open(f)
        hdul.info()
        print(repr(hdul[0].header))
