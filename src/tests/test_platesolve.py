from pathlib import Path

import pytest
from astropy.io.fits import Header

from src.fitstools.platesolve import ASTAPSolver, create_hint, SolverError, SolverFailure, extract_hint


def test_solve_asi183mm():
    headers = solve_testFile("M100_2019-05-02T231819_120sec_LP__-25C_frame9.fit")
    assert headers["PLTSOLVD"] == True
    assert headers["CRVAL1"] == pytest.approx(185.7244712821, 0.001)
    assert headers["CRVAL2"] == pytest.approx(15.81205749322, 0.001)


def test_solve_asi294mc():
    headers = solve_testFile("L_2018-10-23_20-58-50_Bin1x1_240s__-20C.fit")
    assert headers["PLTSOLVD"] == True
    assert headers["CRVAL1"] == pytest.approx(341.8189226876, 0.001)
    assert headers["CRVAL2"] == pytest.approx(58.12444446502, 0.001)


def test_solve_asi294mc_135mm():
    headers = solve_testFile("Sadr Area_2020-05-28T011655_60sec_HaOIII__-15C_frame18.fit")
    assert headers["PLTSOLVD"] == True
    assert headers["CRVAL1"] == pytest.approx(305.185298889526, 0.001)
    assert headers["CRVAL2"] == pytest.approx(40.284375, 0.001)


def test_solve_asi294mc_c925():
    headers = solve_testFile("M57_2020-05-30T022249_30sec_HaOIII_COLD_-17C_frame19.fit")
    assert headers["PLTSOLVD"] == True
    assert headers["CRVAL1"] == pytest.approx(18.8931 * 15, 0.001)
    assert headers["CRVAL2"] == pytest.approx(33.0297, 0.001)


def test_solve_asi294mc_blind():
    hint = create_hint(324, 57)
    headers = solve_testFile("Single__2018-09-24_21-11-00_Bin1x1_120s__-7C.fit", hint)
    assert headers["PLTSOLVD"] == True
    assert headers["CRPIX1"] == 2072.5
    assert headers["CRPIX2"] == 1411.5
    assert headers["CRVAL1"] == pytest.approx(324.676522676, 0.001)
    assert headers["CRVAL2"] == pytest.approx(57.5042416425, 0.001)


# TODO fails because of UTF-8 char in ASTAP output. fixed by astap upgrade
def test_solve_asi290mm_blind():
    hint = extract_hint(Header({"FOCALLEN": 200, "YPIXSZ": 2.9, "NAXIS2": 1088}))
    headers = solve_testFile("asi290_200mm.fits", hint)
    assert headers["PLTSOLVD"] == True
    assert headers["CRPIX1"] == 968.5
    assert headers["CRPIX2"] == 544.5
    assert headers["CRVAL1"] == pytest.approx(251.2511043023, 0.001)
    assert headers["CRVAL2"] == pytest.approx(89.04982022846, 0.001)


def test_error():
    with pytest.raises(SolverError) as excinfo:
        headers = solve_testFile("nosuchFile.fits")
    assert "Error reading image file." in str(excinfo.value)


def test_nosolution():
    with pytest.raises(SolverFailure) as excinfo:
        headers = solve_testFile("DarkFlats_2020-05-30T155512_11.43sec_HaOIII__0C_frame10.fit")
    assert "Failed to solve image" in str(excinfo.value)
    assert "No solution found!" in excinfo.value.log[-1]


def solve_testFile(file, hint=None):
    solver = ASTAPSolver()
    root = Path(__file__).parent
    image_file = Path(root, "test-data", file)
    assert image_file.is_file()
    headers = solver.solve(image_file, hint)
    return headers
