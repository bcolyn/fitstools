#!/usr/bin/env python3
import configparser
import os

from astropy import units as u
from os.path import expanduser
from astropy.coordinates import SkyCoord

from fitstools.util import read_headers, try_header, is_fits


class ReportLine:
    def __init__(self, name, ra, dec, orientation, filter_name, focal_length, exposure):
        self.name = name
        self.ra = ra
        self.dec = dec
        self.orientation = orientation if orientation is not None else ""
        self.filter = filter_name if filter_name is not None else ""
        self.focal_length = focal_length
        self.exposure = exposure

    def to_str(self):
        return "\t".join(
            [self.name, self.filter, self.ra, self.dec, str(self.orientation), str(self.focal_length), "", "", "",
             str(self.exposure)])


def add_to_report(report, object_name, coord, orientation, filter_name, focal_length, exposure):
    key = make_key(object_name, filter_name)
    if key not in report:
        report[key] = ReportLine(object_name, format_ra(coord), format_dec(coord), orientation, filter_name,
                                 focal_length, exposure)
    else:
        line: ReportLine = report[key]
        line.exposure += exposure


def make_key(object_name, filter_name):
    if filter_name is not None:
        return "|".join([object_name, filter_name])
    else:
        return object_name


def summarize_dir(dir: str):
    directory = os.fsencode(dir)
    report = {}

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if dir.lower().endswith("bad") or filename.lower().startswith("bad"):
            continue
        if is_fits(filename):
            print("file:" + filename)
            headers = read_headers(os.path.join(dir, filename))
            if "light" in try_header(headers, "IMAGETYP").lower():
                object_name = try_header(headers, "OBJECT")
                ra = try_header(headers, "OBJCTRA")
                dec = try_header(headers, "OBJCTDEC")
                coord = make_coord(dec, ra)
                orientation = format_orientation(try_header(headers, "ANGLE"))
                filter = try_header(headers, "FILTER")
                focal_length = try_header(headers, "FOCALLEN")
                exposure = try_header(headers, "EXPOSURE", "EXPTIME")
                print(object_name, exposure)
                add_to_report(report, object_name, coord, orientation, filter, focal_length, exposure)

    return report


def make_coord(dec, ra):
    return SkyCoord(ra, dec, unit=(u.hourangle, u.deg)) if ra is not None and dec is not None else None


def format_ra(coord):
    return coord.ra.to_string(unit=u.hour, sep=('h ', '\' ', '"'), precision=0, pad=True) if coord is not None else None


def format_dec(coord):
    return coord.dec.to_string(unit=u.degree, sep=('º ', '\' ', '"'), precision=0) if coord is not None else None


def format_orientation(angle):
    if angle is None:
        return None
    FLEX = 5
    angle = angle + 360 if angle < 0 else angle  # normalize negative angles
    angle = angle - 180 if angle > 180 else angle  # if image is upside-down
    if angle < FLEX or angle > 180 - FLEX:
        return 0
    elif 90 - FLEX < angle < 90 + FLEX:
        return 90
    else:
        return angle


def print_report(report):
    print("report:")
    lines = report.values()
    for line in lines:
        print(line.to_str())


def main():
    script_name = 'summarize_dir'
    conf_file = expanduser("~/fitstools.ini")
    config = init_config(conf_file, script_name)
    ourconfig = config[script_name]
    dir = get_dir(ourconfig)
    if dir:
        store_config(conf_file, config)
        report = summarize_dir(dir)
        print_report(report)


def store_config(conf_file, config):
    with open(conf_file, 'w') as configfile:
        config.write(configfile)


def init_config(conf_file, script_name):
    config = configparser.ConfigParser()
    config.read(conf_file)
    if not config.has_section(script_name):
        config.add_section(script_name)
    return config


def get_dir(config: configparser.ConfigParser):
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    start_dir = config.get('lastdir', '/')
    root.filename = filedialog.askdirectory(initialdir=start_dir, title="Select directory")
    if root.filename:
        config['lastdir'] = root.filename
    return root.filename


if __name__ == "__main__":
    main()
