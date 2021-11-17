import configparser
import os
import subprocess
import tempfile
from pathlib import Path

from astropy.io.fits import Header

from .util import find_header


class ASTAPSolver:
    _tmp_dir: Path
    _exe: str
    _log: bool

    def __init__(self, exe="astap"):
        self._exe = exe
        self._tmp_dir = tempfile.gettempdir()
        self._log = True

    def solve(self, image_file: Path, hint=None) -> Header:
        if not image_file.is_file():
            raise Exception("path is not a file")
        output_file = Path(self._tmp_dir, image_file.name)
        wcs = output_file.with_suffix(".wcs")
        ini = output_file.with_suffix(".ini")
        log = output_file.with_suffix(".log")
        try:
            params = [self._exe, "-f", str(image_file), "-o", str(output_file), "-r", "180", "-s", "100"]
            if hint is not None:
                params.extend(hint)
            if self._log:
                params.append("-log")

            subprocess.run(params)
            if not wcs.exists() and ini.exists():
                self._raise_error(ini, log, image_file)
            return self._read_wcs(wcs)
        finally:
            if wcs.exists():
                wcs.unlink()
            if ini.exists():
                ini.unlink()
            if log.exists():
                log.unlink()

    def _raise_error(self, ini_file, log_file, image_file):
        parser = configparser.ConfigParser()
        with open(ini_file) as stream:
            parser.read_string("[top]\n" + stream.read())
        plain_ini = parser["top"]
        if "ERROR" in plain_ini:
            raise SolverError(plain_ini["ERROR"])
        else:
            log = None
            if self._log:
                try:
                    with open(log_file) as logstream:
                        log = logstream.readlines()
                except:
                    pass
            raise SolverFailure("Failed to solve image " + str(image_file), log)

    def _read_wcs(self, wcs_file):
        return Header.fromtextfile(wcs_file, endcard=False)


def create_hint(ra, dec, radius=None):
    hint = []
    if ra is not None and dec is not None:
        ra_str = str(ra / 15)
        spd_str = str(90 + dec)
        hint.extend(["-ra", ra_str, "-spd", spd_str])
    if radius:
        hint.extend(["-fov", str(radius)])
    return hint


def extract_hint(header: Header):
    ra = find_header(header, "RA", "CRVAL1")
    dec = find_header(header, "DEC", "CRVAL2")
    scale = find_header(header, "SCALE", "PIXSCALE")
    if scale is None:
        focallen = find_header(header, "FOCALLEN")
        pixsize = find_header(header, "YPIXSZ")
        scale = 206.265 * float(pixsize) / float(focallen)
    height = find_header(header, "NAXIS2")
    if scale is not None and height is not None:
        radius = height * scale / 3600
    else:
        radius = None
    return create_hint(ra, dec, radius)


class SolverError(Exception):
    pass


class SolverFailure(Exception):

    def __init__(self, message, log) -> None:
        self.message = message
        self.log = log

    def __str__(self) -> str:
        return self.message


def main():
    # f = r"C:\TEMP\M101_2020-03-28T025125_60sec_LP__-15C_frame20.bak"
    # f = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-17\M33\L_2018-09-18_01-00-46_Bin1x1_240s__-15C.fit"
    # f = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-26\NGC 6888-Cresent\set1\L_2018-09-26_23-00-32_Bin1x1_240s__-24C.fit"
    # f = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-17\Test\Single__2018-09-17_21-24-47_Bin1x1_1s__5C.fit"
    # f = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-24\Test\Single__2018-09-24_21-11-00_Bin1x1_120s__-7C.fit"
    # f = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-27\M27\L_2018-09-28_00-50-43_Bin1x1_120s__-20C.fit"
    # f = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-12-13\M76\L_2018-12-13_18-38-23_Bin1x1_120s__-29C.fit"
    # f = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-11-18\M42-Orion Nebula\L_2018-11-19_00-14-46_Bin1x1_60s__-22C.fit"
    # f = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-11-18\M42-Orion Nebula\BAD\L_2018-11-19_00-12-38_Bin1x1_60s__-15C.fit"

    images = [
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-11-18\B3-Horsehead\L_2018-11-19_00-35-33_Bin1x1_240s__-25C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-11-17\Single__2018-11-17_17-48-48_Bin1x1_1s__11C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-10-23\Single__2018-10-23_17-24-27_Bin1x1_2s__14C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-10-15\Single__2018-10-15_19-55-58_Bin1x1_5s__17C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-10-09\test\Single__2018-10-09_22-29-11_Bin1x1_5s__8C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-10-09\NGC 869-NGC 884-Double Cluster\L_2018-10-09_22-43-13_Bin1x1_120s__-21C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-10-05\NGC 7635-Bubble\L_2018-10-05_21-50-05_Bin1x1_240s__-20C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-10-05\M13\L_2018-10-05_21-11-22_Bin1x1_120s__-21C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-10-04\IC 5146-Cocoon\L_2018-10-05_00-15-16_Bin1x1_120s__-20C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-27\NGC 6888-Cresent\L_2018-09-27_21-54-48_Bin1x1_240s__-20C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-27\M27\L_2018-09-28_00-50-43_Bin1x1_120s__-20C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-26\NGC 6888-Cresent\set2\L_2018-09-27_00-36-15_Bin1x1_240s__-24C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-26\NGC 6888-Cresent\set1\L_2018-09-26_23-00-32_Bin1x1_240s__-24C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-24\Test\Single__2018-09-24_21-11-00_Bin1x1_120s__-7C.fit",
        r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-17\Test\Single__2018-09-17_21-24-47_Bin1x1_1s__5C.fit"
    ]

    image_dir = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-10-04\IC 5146-Cocoon"
    image_dir = r"E:\Astro_Archief\Deep Sky\ZWO_ASI294MC_Pro\2018-09-26\NGC 6888-Cresent\set2"

    solver = ASTAPSolver()
    hint = None

    f: os.DirEntry
    for f in os.scandir(image_dir):
        image = Path(f)
        if image.name.startswith("F"):
            continue
        print(str(image.resolve()))

        try:
            headers = solver.solve(image, hint)
            hint = extract_hint(headers)
            for header in headers:
                print(header + "\t" + str(headers[header]))
        except Exception as ex:
            print("E: failed to solve: " + str(ex))
            raise ex
        print("-----------------------------")


if __name__ == "__main__":
    main()
