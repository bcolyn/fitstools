import hashlib
import os
from os.path import expanduser

import yaml


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


def sha1sum(path):
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        while True:
            data = f.read(65536)  # 64kb chunks
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def is_master(name: str):
    return name.endswith(".fits") and \
           (name.startswith("MD-ISO")
            or name.startswith("MDF-ISO")
            or name.startswith("BPM")
            or name.startswith("MF-ISO"))


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