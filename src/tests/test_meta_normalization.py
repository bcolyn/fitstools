from pathlib import Path
from dateutil import parser
import pytest
from astropy.io.fits import Header

from fitstools.analysis.metadata import MetadataAnalyser
from fitstools.model import ImageType

from . import sample_headers


def test_sgp_meta():
    header = Header.fromstring(sample_headers.header_sgp_fixed_wcs, "\n")
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == ImageType.LIGHT
    assert results.camera_name == "ZWO ASI294MC Pro"
    assert results.gain == 120
    assert results.exposure == 30.0
    assert results.camera_temperature == -17.5
    assert results.object_name == "M57"
    assert results.filter == "HaOIII"
    assert results.xbin == 1
    assert results.ybin == 1
    assert results.offset == 30
    assert results.telescope == "EQMOD ASCOM HEQ5/6"
    assert results.datetime_local == parser.parse("2020-05-30T02:22:49.096882")
    assert results.datetime_utc == parser.parse("2020-05-30T00:22:49.096882")


def test_apt_meta():
    header = Header.fromstring(sample_headers.header_apt, "\n")
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == ImageType.LIGHT
    assert results.camera_name == "ZWO ASI294MC Pro"
    assert results.gain == 120
    assert results.exposure == 240
    assert results.camera_temperature == -15.0
    assert results.object_name == "TEST"
    assert results.filter is None
    assert results.xbin == 1
    assert results.ybin == 1
    assert results.offset is None
    assert results.telescope == "EQMOD HEQ5/6"
    assert results.datetime_local is None
    assert results.datetime_utc == parser.parse("2018-09-17T21:04:46")


def test_nina_meta():
    header = Header.fromstring(sample_headers.header_nina, "\n")
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == ImageType.LIGHT
    assert results.camera_name == "ZWO ASI294MC Pro"
    assert results.gain == 120
    assert results.exposure == 30
    assert results.camera_temperature == -10.0
    assert results.object_name == "MarsM45"
    assert results.filter is None
    assert results.xbin == 1
    assert results.ybin == 1
    assert results.offset == 30
    assert results.telescope is None
    assert results.datetime_local == parser.parse("2021-03-02T21:19:00.455")
    assert results.datetime_utc == parser.parse("2021-03-02T20:19:00.455")

def test_maximdl_meta():
    header = Header.fromstring(sample_headers.header_maximdl, "\n")
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == ImageType.LIGHT
    assert results.camera_name == "Apogee USB/Net"
    assert results.gain is None
    assert results.exposure == 300
    assert results.camera_temperature == pytest.approx(-35.0, 0.1)
    assert results.object_name == "m17"
    assert results.filter == "SII"
    assert results.xbin == 1
    assert results.ybin == 1
    assert results.offset is None
    assert results.telescope == "iTelescope 33"
    assert results.datetime_local is None
    assert results.datetime_utc == parser.parse("2018-07-04T14:03:03")


def test_no_meta():
    header = Header()
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == ImageType.UNKNOWN
    assert results.camera_name is None
