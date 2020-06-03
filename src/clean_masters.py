#!/usr/bin/env python3
from os import DirEntry

from src.fitstools import walk_dir, sha1sum, is_master, BaseReporter
from src.Config import Config

import os
import functools


class Reporter(BaseReporter):

    def __init__(self):
        super().__init__()
        self.__known_count = 0
        self.__unknown_counts = {}
        self.__unknown_locations = {}

    def unknown_master(self, file, hex_sum):
        self.dot()
        if hex_sum not in self.__unknown_counts:
            self.__unknown_counts[hex_sum] = 1
            self.__unknown_locations[hex_sum] = file.path
        else:
            self.__unknown_counts[hex_sum] += 1

    def known_master(self, file, hex_sum):
        self.dot()
        self.__known_count += 1

    def report(self):
        print("done.")
        print("Known masters removed:", self.__known_count)
        print("Unknown masters remaining:", sum(map(lambda kv: kv[1], self.__unknown_counts.items())))
        print("Top unknown masters:")
        unknowns = sorted(self.__unknown_counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        topN = unknowns[0:10]
        for (key, value) in topN:
            print("\t".join([str(value), key, self.__unknown_locations[key]]))


class MasterLib:
    def __init__(self, conf):
        self.__conf = conf
        self.__hashes = {}
        self.__load_data()

    def __parse_line(self, line):
        (key, fname) = line.split(None, 2)
        self.__hashes[key] = fname

    def __load_data(self):
        hash_file = self.__conf.data.masters.sha1sum_file
        if os.path.isfile(hash_file):
            with(open(hash_file, 'r')) as stream:
                line = stream.readline()
                while line:
                    self.__parse_line(line)
                    line = stream.readline()

    def has_master(self, checksum):
        return checksum in self.__hashes


def check_master(lib: MasterLib, reporter: Reporter, file: DirEntry):
    if is_master(file.name):
        hex_sum = sha1sum(file.path)

        if lib.has_master(hex_sum):
            mk_chksum(file.path, hex_sum)
            reporter.known_master(file, hex_sum)
            remove_file(file.path)
        else:
            reporter.unknown_master(file, hex_sum)


def remove_file(path):
    os.unlink(path)


def trash_file(path):
    dir_name = os.path.dirname(path)
    trash = os.sep.join([dir_name, ".Trash"])
    trashed_path = os.sep.join([trash, os.path.basename(path)])
    if not os.path.isdir(trash):
        os.mkdir(trash)
    os.rename(path, trashed_path)
    print("moved {} to {}".format(path, trashed_path))


def mk_chksum(path, hex_sum):
    sum_file = path + ".sha1sum"
    with open(sum_file, 'w+') as f:
        f.write(hex_sum + " *" + os.path.basename(path) + "\n")


def main():
    """ Main entry point of the app """
    conf = Config()
    lib = MasterLib(conf)
    reporter = Reporter()
    walk_dir(functools.partial(check_master, lib, reporter), os.path.curdir)
    reporter.report()


if __name__ == "__main__":
    main()
