import pytest

from src.fitstools.creators import *


def test_find_sgp():
    headers = {"CREATOR": 'Sequence Generator Pro v3.0.3.165'}
    creator = Creator.find_creator(headers)
    assert creator == Creator.SequenceGeneratorPro


def test_find_apt():
    headers = {"SWCREATE": 'Astro Photography Tool - APT v.3.54.1'}
    creator = Creator.find_creator(headers)
    assert creator == Creator.AstroPhotographyTool


def test_find_not_supported():
    headers = {"FOO": "Careful man, there's a beverage here"}
    with pytest.raises(RuntimeError) as excinfo:
        Creator.find_creator(headers)
        assert "unsupported software" in str(excinfo.value)


def test_check_sanity():
    headers = {"CREATOR": 'Sequence Generator Pro v3.0.3.165'}
    support: SGPSupport = Creator.find_creator(headers).support()
    with pytest.raises(RuntimeError) as excinfo:
        support.check_sanity(headers)
        assert "missing required header: IMAGETYP" in str(excinfo.value)
