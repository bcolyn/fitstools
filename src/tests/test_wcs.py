from math import cos, radians
from math import sin
from pathlib import Path

import pytest
from astropy.coordinates import Angle
from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS

from fitstools.platesolve import ASTAPSolver


def test_solve_asi294mc_135mm():
    headers = solve_test_file("Sadr Area_2020-05-28T011655_60sec_HaOIII__-15C_frame18.fit")
    assert headers["PLTSOLVD"] == True
    assert headers["CRVAL1"] == pytest.approx(305.185298889526, 0.001)
    assert headers["CRVAL2"] == pytest.approx(40.284375, 0.001)


def test_fix_wcs():
    #fname = "M57_2020-05-30T022249_30sec_HaOIII_COLD_-17C_frame19.fit"
    #fname = "Pacman OIII_2019-09-20T230611_60sec_OIII__-15C_frame12.fit"
    fname = "Sadr Area_2020-05-28T011655_60sec_HaOIII__-15C_frame18.fit"
    # fname = "L_2018-10-23_20-58-50_Bin1x1_240s__-20C.fit"
    solved_headers = solve_test_file(fname)
    print_header(solved_headers)
    solved_wcs = WCS(solved_headers)
    solved_wcs.printwcs()
    print_footprint(solved_wcs)

    hdu = fits.open(resource_file(fname))[0]
    header = hdu.header
    fixup_wcs(header)
    print_header(header)
    wcs = WCS(header)
    wcs.printwcs()

    print_footprint(wcs)


def fixup_wcs(header):
    crota = header["POSANGLE"] - 180
    crota_rad = radians(crota)
    cdelt = header["PIXSCALE"] / 3600.0
    flipped = header["FLIPPED"]
    header["CUNIT1"] = "deg"
    header["CROTA1"] = crota
    header["CROTA2"] = crota
    header["CDELT1"] = cdelt
    header["CDELT2"] = cdelt
    if not flipped:
        header["CD1_1"] = cdelt * cos(crota_rad)
        header["CD1_2"] = cdelt * sin(crota_rad)
        header["CD2_1"] = -cdelt * sin(crota_rad)
        header["CD2_2"] = cdelt * cos(crota_rad)
    else:  # RASA and such
        header["CD1_1"] = -cdelt * cos(crota_rad)
        header["CD1_2"] = cdelt * sin(crota_rad)
        header["CD2_1"] = cdelt * sin(crota_rad)
        header["CD2_2"] = cdelt * cos(crota_rad)


def print_footprint(wcs):
    print("\nFOOTPRINT")
    footprint = wcs.calc_footprint()
    labels = ["top-left", "bottom-left", "bottom-right", "top-right"]
    for (ra, dec) in footprint:
        print(labels.pop(0) + "\t" + Angle(ra * u.deg).to_string(unit=u.hour) + "\t" + Angle(dec * u.deg).to_string())


def resource_file(file):
    return Path("test-data", file)


def solve_test_file(file, hint=None):
    solver = ASTAPSolver()
    image_file = Path("test-data", file)
    headers = solver.solve(image_file, hint)
    return headers


def print_header(headers):
    print("\nHEADERS:\n")
    for header in headers:
        print(header.ljust(8) + "\t" + str(headers[header]))
