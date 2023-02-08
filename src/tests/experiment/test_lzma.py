import gzip
import lzma
from io import BytesIO
from pathlib import Path

import numpy
from astropy.io import fits
from astropy.io.fits import HDUList


def test_read_lzma_header_buffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit.xz'
    with lzma.open(filename, mode="rb") as f:
        bytes = BytesIO(f.read())
    hdul: HDUList = fits.open(bytes)
    hdul.info()
    print(repr(hdul[0].header))


def test_read_lzma_header_nobuffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit.xz'
    with lzma.open(filename, mode="rb") as f:
        hdul: HDUList = fits.open(f)
        hdul.info()
        print(repr(hdul[0].header))


def test_read_lzma_all_buffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit.xz'
    with lzma.open(filename, mode="rb") as f:
        bytes = BytesIO(f.read())
    hdul: HDUList = fits.open(bytes, memmap=False, cache=False, lazy_load_hdus=True)
    hdul.info()
    print(repr(hdul[0].header))
    print("data average %d" % numpy.average(hdul[0].data))
    print("data median %d" % numpy.median(hdul[0].data))


def test_read_lzma_all_nobuffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit.xz'
    with lzma.open(filename, mode="rb") as f:
        hdul: HDUList = fits.open(f, memmap=False, cache=False, lazy_load_hdus=True)
        hdul.info()
        print(repr(hdul[0].header))
        print("data average %d" % numpy.average(hdul[0].data))
        print("data median %d" % numpy.median(hdul[0].data))


def test_read_gzip_header_buffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit.gz'
    with gzip.open(filename, mode="rb") as f:
        buffer = BytesIO(f.read())
    hdul: HDUList = fits.open(buffer, memmap=False, cache=False, lazy_load_hdus=True)
    hdul.info()
    print(repr(hdul[0].header))


def test_read_gzip_header_nobuffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit.gz'
    with gzip.open(filename, mode="rb") as f:
        hdul: HDUList = fits.open(f, memmap=False, cache=False, lazy_load_hdus=True)
        hdul.info()
        print(repr(hdul[0].header))


def test_read_gzip_all_buffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit.gz'
    with gzip.open(filename, mode="rb") as f:
        buffer = BytesIO(f.read())
    hdul: HDUList = fits.open(buffer, memmap=False, cache=False, lazy_load_hdus=True)
    hdul.info()
    print(repr(hdul[0].header))
    print("data average %d" % numpy.average(hdul[0].data))
    print("data median %d" % numpy.median(hdul[0].data))


def test_read_gzip_all_nobuffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit.gz'
    with gzip.open(filename, mode="rb") as f:
        hdul: HDUList = fits.open(f, memmap=False, cache=False, lazy_load_hdus=True)
        hdul.info()
        print(repr(hdul[0].header))
        print("data average %d" % numpy.average(hdul[0].data))
        print("data median %d" % numpy.median(hdul[0].data))


def test_read_uncompressed_header_nobuffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit'
    with open(filename, mode="rb") as f:
        hdul: HDUList = fits.open(f, memmap=False, cache=False, lazy_load_hdus=True)
        hdul.info()
        print(repr(hdul[0].header))


def test_read_uncompressed_header_buffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit'
    with open(filename, mode="rb") as f:
        buffer = BytesIO(f.read())
    hdul: HDUList = fits.open(buffer, memmap=False, cache=False, lazy_load_hdus=True)
    hdul.info()
    print(repr(hdul[0].header))


def test_read_uncompressed_all_nobuffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit'
    with open(filename, mode="rb") as f:
        hdul: HDUList = fits.open(f, memmap=False, cache=False, lazy_load_hdus=True)
        hdul.info()
        print(repr(hdul[0].header))
        print("data average %d" % numpy.average(hdul[0].data))
        print("data median %d" % numpy.median(hdul[0].data))


def test_read_uncompressed_all_buffer():
    filename = r'E:\TEMP\IC 342_2019-12-02T022653_60sec_LP__-15C_frame6.fit'
    with open(filename, mode="rb") as f:
        buffer = BytesIO(f.read())
    hdul: HDUList = fits.open(buffer, memmap=False, cache=False, lazy_load_hdus=True)
    hdul.info()
    print(repr(hdul[0].header))
    print("data average %d" % numpy.average(hdul[0].data))
    print("data median %d" % numpy.median(hdul[0].data))


def resolve_test_data(file):
    root = Path(__file__).parent
    path = Path(root, "../test-data", file)
    assert path.exists()
    return path
