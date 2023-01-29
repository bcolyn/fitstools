from pathlib import Path

import pytest
from astropy.io.fits import Header

from fitstools.analysis.metadata import MetadataAnalyser
from fitstools.model import FrameType

from . import sample_headers


def test_sgp_meta():
    header = Header.fromstring(sample_headers.header_sgp_fixed_wcs, "\n")
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == FrameType.LIGHT
    assert results.camera == "ZWO ASI294MC Pro"
    assert results.gain == 120
    assert results.exposure == 30.0
    assert results.temp == -17.5
    assert results.object_name == "M57"
    assert results.filter == "HaOIII"
    assert results.xbin == 1
    assert results.ybin == 1
    assert results.offset == 30
    assert results.telescope == "EQMOD ASCOM HEQ5/6"


def test_apt_meta():
    header = Header.fromstring(sample_headers.header_apt, "\n")
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == FrameType.LIGHT
    assert results.camera == "ZWO ASI294MC Pro"
    assert results.gain == 120
    assert results.exposure == 240
    assert results.temp == -15.0
    assert results.object_name == "TEST"
    assert results.filter is None
    assert results.xbin == 1
    assert results.ybin == 1
    assert results.offset is None
    assert results.telescope == "EQMOD HEQ5/6"


def test_nina_meta():
    header = Header.fromstring(sample_headers.header_nina, "\n")
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == FrameType.LIGHT
    assert results.camera == "ZWO ASI294MC Pro"
    assert results.gain == 120
    assert results.exposure == 30
    assert results.temp == -10.0
    assert results.object_name == "MarsM45"
    assert results.filter is None
    assert results.xbin == 1
    assert results.ybin == 1
    assert results.offset == 30
    assert results.telescope is None


def test_maximdl_meta():
    header = Header.fromstring(sample_headers.header_maximdl, "\n")
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == FrameType.LIGHT
    assert results.camera == "Apogee USB/Net"
    assert results.gain is None
    assert results.exposure == 300
    assert results.temp == pytest.approx(-35.0, 0.1)
    assert results.object_name == "m17"
    assert results.filter == "SII"
    assert results.xbin == 1
    assert results.ybin == 1
    assert results.offset is None
    assert results.telescope == "iTelescope 33"


def test_no_meta():
    header = Header()
    results = MetadataAnalyser.normalize(header, Path("dummyFile.fit"))
    assert results.img_type == FrameType.UNKNOWN
    assert results.camera is None
