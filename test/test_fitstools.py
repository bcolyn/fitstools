from src.fitstools import marked_bad


def test_marked_bad():
    assert marked_bad("BAD_fits.blah.fits") is True

def test_not_marked_bad():
    assert marked_bad("M51_fits.blah.fits") is False
