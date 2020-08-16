import os
from os.path import expanduser

import yaml


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
