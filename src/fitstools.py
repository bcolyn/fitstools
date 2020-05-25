import hashlib
import os
from os.path import expanduser

import yaml
from astropy.io import fits
from astropy.io.fits import Header, VerifyError, Card


class Config:
    class Obj(object):
        def __init__(self, d):
            for a, b in d.items():
                if isinstance(b, (list, tuple)):
                    setattr(self, a, [Config.Obj(x) if isinstance(x, dict) else x for x in b])
                else:
                    setattr(self, a, Config.Obj(b) if isinstance(b, dict) else b)

    @staticmethod
    def __defaults():
        return {
            "test": "foo",
            "masters": {
                "test": 2
            }
        }

    def __init__(self):
        data = self.__defaults()
        home = expanduser("~")
        conf_file = os.sep.join([home, ".fitstools.yaml"])
        if os.path.isfile(conf_file):
            with open(conf_file, 'r') as stream:
                try:
                    yml = yaml.safe_load(stream)
                    data.update(yml)
                    self.data = Config.Obj(data)
                except yaml.YAMLError as exc:
                    raise exc


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


def memoize(f):
    memo = {}

    def helper(x):
        if x not in memo:
            memo[x] = f(x)
        return memo[x]

    return helper


class BaseReporter:
    def __init__(self):
        self.__dots = 0

    def dot(self):
        if self.__dots < 79:
            print(".", end='')
            self.__dots += 1
        else:
            print(".")
            self.__dots = 0


def read_headers(file):
    with fits.open(file) as hdul:
        return hdul[0].header  # support more than 1 HDU?


def try_header(headers: Header, *fieldnames):
    for fieldname in fieldnames:
        if fieldname in headers:
            try:
                return headers[fieldname]
            except VerifyError:
                card: Card = headers.cards[fieldname]
                card._image = card._image.replace('\t', ' ')  # tabs, even if non-printable, are common in my FITS files
                return card.value
    return None
