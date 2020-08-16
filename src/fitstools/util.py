import hashlib
import os

from astropy.io import fits
from astropy.io.fits import Header, VerifyError, Card


# deprecated
def walk_dir(cb, start):
    skip_dirs = []  # [".Trash"]
    queue = [start]
    while len(queue) > 0:
        d = queue.pop()
        for f in os.scandir(d):
            if f.is_dir():
                if not (f.name in skip_dirs):
                    queue.append(f)
                else:
                    pass
                    # print("skipping dir", f.name)
            if f.is_file():
                cb(f)


def gather_files(cb, start, file_filter=lambda f: True, dir_filter=lambda d: True):
    queue = [start]
    while len(queue) > 0:
        d = queue.pop()
        files = []
        for f in os.scandir(d):
            if f.is_dir():
                if dir_filter(d):
                    queue.append(f)
                else:
                    pass
            if f.is_file():
                if file_filter(f):
                    files.append(f)
        if not len(files) == 0:
            cb(files)


def sha1sum(path):
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        while True:
            data = f.read(65536)  # 64kb chunks
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def is_fits(f: os.DirEntry):
    filename = os.fsdecode(f)
    return filename.lower().endswith(".fit") or filename.lower().endswith(".fits")


def marked_bad(f: os.DirEntry):
    """" skips over files that are marked bad """
    filename = os.fsdecode(f)
    return filename.lower().startswith("bad")


def is_master(name: str):
    return name.endswith(".fits") and \
           (name.startswith("MD-ISO")
            or name.startswith("MDF-ISO")
            or name.startswith("BPM")
            or name.startswith("MF-ISO"))





def read_headers(file: object) -> Header:
    with fits.open(file, mode='readonly') as hdul:
        return hdul[0].header  # support more than 1 HDU?


def find_header(headers: Header, *fieldnames):
    card = find_header_card(headers, *fieldnames)
    if card is None:
        return None
    return card.value


def find_header_card(headers: Header, *fieldnames):
    for fieldname in fieldnames:
        if fieldname in headers:
            return headers.cards[fieldname]
    return None


def try_header(headers: Header, *fieldnames):
    card = find_header_card(headers, *fieldnames)
    if card is None:
        return None
    try:
        return card.value
    except VerifyError:
        card._image = card._image.replace('\t', ' ')  # tabs, even if non-printable, are common in my FITS files
        return card.value
